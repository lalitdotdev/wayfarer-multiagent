# main.py
import os
import json
import re
import sys
from typing import TypedDict, Annotated
import operator

import psycopg
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages import (
    AnyMessage,
    HumanMessage,
    AIMessage,
    SystemMessage,
)
from langchain_groq import ChatGroq

from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# LLM Config
llm = ChatGroq(
    model="llama-3.3-70b-versatile"
)

# Robust State Schema
# NOTE: llm_calls now uses operator.add as its reducer. This is REQUIRED
# because flight_agent and hotel_agent run in parallel (fan-out from
# planner_agent) and both may write to llm_calls in the same superstep.
# Without a reducer, LangGraph raises InvalidUpdateError since it can't
# reconcile two concurrent writes to the same key.
#
# IMPORTANT: because the reducer is operator.add, every node must return
# the DELTA (how many LLM calls it made in this invocation), NOT the
# running total. LangGraph sums the deltas from all nodes in a step
# automatically.
class TravelState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str
    destination: str
    departure_city: str
    dep_iata: str
    arr_iata: str
    flight_search_query: str
    hotel_search_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: Annotated[int, operator.add]
    is_travel_related: bool

# --- AGENT FUNCTIONS ---

def router_agent(state: TravelState):
    """
    Classify whether the latest user query is travel-related or general chit-chat.
    """
    user_query = state["user_query"]
    prompt = f"""
    You are an intent classifier for a Travel Booking assistant.
    Analyze the user's latest query and decide if they are asking for travel suggestions, flight info, hotel info, itineraries, or modifying an existing travel plan.
    
    User Query: {user_query}
    
    Respond with 'TRAVEL' if it's travel-related (flights, hotels, destinations, itinerary planning).
    Respond with 'OTHER' if it is general chit-chat, a greeting, a test, code, math, or anything else unrelated to planning a trip.
    
    Return ONLY 'TRAVEL' or 'OTHER'. Do not include any other text or explanation.
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content.strip().upper()
    is_travel = "TRAVEL" in content

    return {
        "is_travel_related": is_travel,
        "llm_calls": 1
    }

def route_intent(state: TravelState):
    """
    Routing edge logic based on router_agent output.
    """
    if state.get("is_travel_related", True):
        return "planner_agent"
    return "chitchat_agent"

def chitchat_agent(state: TravelState):
    """
    Handles greetings, conversational chit-chat, or general assistance,
    while gently steering the user back to travel booking.
    """
    user_query = state["user_query"]
    response = llm.invoke([
        SystemMessage(content=(
            "You are Wayfarer's helpful assistant. You handle greetings and general chit-chat warmly, "
            "but always politely guide the user back to asking about travel booking, flights, hotels, "
            "or itineraries since that is your specialty."
        )),
        HumanMessage(content=user_query)
    ])
    return {
        "messages": [response],
        "llm_calls": 1
    }

def planner_agent(state: TravelState):
    """
    Extracts structured query parameters and airport codes from the user query and chat history.
    """
    user_query = state["user_query"]
    messages = state["messages"]

    history_str = ""
    for m in messages[:-1]:
        role = "User" if isinstance(m, HumanMessage) else "Assistant"
        history_str += f"{role}: {m.content}\n"

    prompt = f"""
    You are a travel details extractor. Analyze the current query and conversational history to produce a clean JSON object containing travel details.
    
    Current User Query: {user_query}
    
    Conversation History:
    {history_str}
    
    Produce a JSON object with exactly the following fields:
    - destination: Destination city/country name (string, or null if unknown)
    - departure_city: Starting city/airport name (string, or null if unknown)
    - dep_iata: 3-letter IATA airport code for departure (string, or null if unknown)
    - arr_iata: 3-letter IATA airport code for destination (string, or null if unknown)
    - flight_search_query: Search query for flights (string)
    - hotel_search_query: Search query for hotels (string)
    
    Return ONLY valid JSON. Do not include markdown code block wrappers (like ```json) or any explanations.
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    content = response.content.strip()

    # Strip markdown block wrappers if present
    if content.startswith("```"):
        content = re.sub(r"^```[a-zA-Z]*\n", "", content)
        content = re.sub(r"\n```$", "", content)
    content = content.strip()

    try:
        data = json.loads(content)
    except Exception:
        data = {}

    return {
        "destination": data.get("destination") or state.get("destination") or "unknown",
        "departure_city": data.get("departure_city") or state.get("departure_city") or "unknown",
        "dep_iata": data.get("dep_iata") or state.get("dep_iata") or "unknown",
        "arr_iata": data.get("arr_iata") or state.get("arr_iata") or "unknown",
        "flight_search_query": data.get("flight_search_query") or user_query,
        "hotel_search_query": data.get("hotel_search_query") or f"best hotels in {data.get('destination', user_query)}",
        "llm_calls": 1
    }

def flight_agent(state: TravelState):
    """
    Fetches flight schedules and fares using flight_tool.
    Note: this node calls an external flight-search tool, not the LLM,
    so it does not increment llm_calls.
    """
    dest = state.get("destination", "unknown")
    if dest == "unknown":
        return {
            "flight_results": "Destination unknown. Skipping flight search.",
            "messages": [AIMessage(content="[Flight Agent] No destination found to search flights.")]
        }

    query = state.get("flight_search_query", state["user_query"])
    dep = state.get("dep_iata")
    arr = state.get("arr_iata")

    flight_data = search_flights(
        query=query,
        dep_iata=None if dep == "unknown" else dep,
        arr_iata=None if arr == "unknown" else arr
    )
    return {
        "flight_results": flight_data,
        "messages": [AIMessage(content="[Flight Agent] Searched and fetched flight options.")]
    }

def hotel_agent(state: TravelState):
    """
    Fetches hotel reviews and details using tavily search.
    Note: this node calls an external search tool, not the LLM,
    so it does not increment llm_calls.
    """
    dest = state.get("destination", "unknown")
    if dest == "unknown":
        return {
            "hotel_results": "Destination unknown. Skipping hotel search.",
            "messages": [AIMessage(content="[Hotel Agent] No destination found to search hotels.")]
        }

    query = state.get("hotel_search_query", f"best hotels in {dest}")
    hotel_data = tavily_search(query)
    return {
        "hotel_results": hotel_data,
        "messages": [AIMessage(content="[Hotel Agent] Searched and fetched hotel options.")]
    }

def itinerary_agent(state: TravelState):
    """
    Synthesizes flights and hotels into a personalized, beautiful narrative itinerary.
    """
    if state.get("destination", "unknown") == "unknown":
        return {
            "itinerary": "No travel destination specified.",
            "messages": [AIMessage(content="[Itinerary Agent] Skipped itinerary generation.")]
        }

    prompt = f"""
    Create a travel itinerary.
    User Query: {state['user_query']}
    Destination: {state['destination']}
    Departure City: {state['departure_city']}
    
    Flight Options:
    {state['flight_results']}
    
    Hotel Options:
    {state['hotel_results']}
    """

    response = llm.invoke([
        SystemMessage(
            content="""
You are a world-class travel agent AI. Your mission is to design perfect, human-centric travel itineraries by synthesizing flight data, hotel suggestions, and the user’s core request.

STYLE GUIDE FOR ITINERARY:
- Be warm, conversational, and human. Avoid robotic phrasing.
- Use engaging storytelling rather than bullet points (unless the user explicitly requests bullets).
- Incorporate the flight information smoothly — for example: "Since you’re flying on [Airline] arriving at [Time], you’ll land refreshed and ready to explore."
- Use the hotel information contextually: "Once you settle into [Hotel Name], known for its [Key Feature], you’ll have a perfect base for..."
- Balance structure with warmth:
  * Start with a friendly opening acknowledging their travel goals.
  * Lay out the trip day by day using short narrative paragraphs.
  * Blend practical suggestions with lifestyle touches (e.g., "grab a coffee at that quaint cafe near your hotel," "take an evening stroll along the beach").
  * End with a warm sign-off and clear next steps if applicable.

FORMATTING:
- Use markdown for readability (bolding, short headings).
- Keep paragraphs under 3–4 lines maximum.
- Make the tone feel like a personalized recommendation from a friend who is an expert in travel.
            """
        ),
        HumanMessage(content=prompt)
    ])

    return {
        "itinerary": response.content,
        "messages": [response],
        "llm_calls": 1
    }

def final_agent(state: TravelState):
    """
    Packages the generated itinerary and summaries into a friendly final user response.
    """
    if not state.get("is_travel_related", True):
        return {}

    final_prompt = f"""
    Synthesize a final response for the user's travel request.
    
    Proposed Itinerary:
    {state['itinerary']}
    
    Provide the finalized response containing the itinerary, flight details, and hotel suggestions, wrapped beautifully.
    """
    response = llm.invoke([HumanMessage(content=final_prompt)])

    return {
        "messages": [response],
        "llm_calls": 1
    }

# --- GRAPH BUILDER ---

graph = StateGraph(TravelState)

# Add Nodes
graph.add_node("router_agent", router_agent)
graph.add_node("chitchat_agent", chitchat_agent)
graph.add_node("planner_agent", planner_agent)
graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

# Define Control Flow Graph Edges
graph.add_edge(START, "router_agent")
graph.add_conditional_edges(
    "router_agent",
    route_intent,
    {
        "planner_agent": "planner_agent",
        "chitchat_agent": "chitchat_agent"
    }
)

# Chitchat ends workflow
graph.add_edge("chitchat_agent", END)

# Parallel (fan-out) execution from planner
graph.add_edge("planner_agent", "flight_agent")
graph.add_edge("planner_agent", "hotel_agent")

# Parallel merge (fan-in) into itinerary agent
graph.add_edge("flight_agent", "itinerary_agent")
graph.add_edge("hotel_agent", "itinerary_agent")

# Finalize
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)

# Persistent Database connection pool
pool = ConnectionPool(
    conninfo=DATABASE_URL,
    max_size=10,
    kwargs={"autocommit": True, "row_factory": dict_row}
)
checkpointer = PostgresSaver(pool)
checkpointer.setup()

# Compile the final app
app = graph.compile(checkpointer=checkpointer)

# --- CLI UI LOGIC ---

def print_banner():
    banner = """
    \033[96m╔════════════════════════════════════════════════════════════════════════════════╗
    ║                                                                                ║
    ║    ✦  W A Y F A R E R  ✦                                                       ║
    ║    Multi-Agent Travel Planner & Concierge (Postgres Memory enabled)            ║
    ║                                                                                ║
    ╚════════════════════════════════════════════════════════════════════════════════╝\033[0m
    """
    print(banner)

def print_agent_step(agent_name: str, message: str):
    print(f"\033[95m[✦ {agent_name}]\033[0m {message}")
    sys.stdout.flush()

if __name__ == "__main__":
    print_banner()

    # Session config with thread_id for state memory persistence
    config = {
        "configurable": {
            "thread_id": "session_user_lalit"
        }
    }

    print("\033[90mSession started. Type 'exit' or 'quit' to end.\033[0m\n")

    while True:
        try:
            user_input = input("\033[93mYou: \033[0m").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("\n\033[96mThank you for using Wayfarer. Safe travels!\033[0m")
                break

            # Initial state
            inputs = {
                "messages": [HumanMessage(content=user_input)],
                "user_query": user_input,
                "destination": "unknown",
                "departure_city": "unknown",
                "dep_iata": "unknown",
                "arr_iata": "unknown",
                "flight_search_query": "",
                "hotel_search_query": "",
                "flight_results": "",
                "hotel_results": "",
                "itinerary": "",
                "llm_calls": 0,
                "is_travel_related": True
            }

            print("\n\033[90m⚙ Executing multi-agent pipeline...\033[0m")

            # Stream execution nodes in real-time
            for event in app.stream(inputs, config=config):
                for node, output in event.items():
                    if node == "router_agent":
                        is_travel = output.get("is_travel_related", True)
                        print_agent_step("Intent Router", f"Checking query... (Travel Request: {is_travel})")
                    elif node == "planner_agent":
                        print_agent_step("Planner Agent", f"Extracted -> Destination: {output.get('destination')}, From: {output.get('departure_city')}")
                    elif node == "flight_agent":
                        print_agent_step("Flight Agent", "Fetching airline itineraries...")
                    elif node == "hotel_agent":
                        print_agent_step("Hotel Agent", "Running accommodation searches...")
                    elif node == "itinerary_agent":
                        print_agent_step("Itinerary Agent", "Designing personalized itinerary narrative...")
                    elif node == "chitchat_agent":
                        print_agent_step("Concierge", "Generating conversational chat response...")
                    elif node == "final_agent":
                        print_agent_step("Synthesizer", "Wrapping final recommendation packages...")

            # Retrieve final state from history
            final_state = app.get_state(config)
            final_messages = final_state.values.get("messages", [])

            if final_messages:
                last_msg = final_messages[-1].content
                print(f"\n\033[92m✦ WAYFARER CONCIERGE ✦\033[0m\n")
                print(last_msg)
                print("\n" + "\033[90m─\033[0m"*60 + "\n")
            else:
                print("\n\033[91mError: No agent response generated.\033[0m")

        except KeyboardInterrupt:
            print("\n\033[96mThank you for using Wayfarer. Safe travels!\033[0m")
            break
        except Exception as e:
            print(f"\n\033[91mAn error occurred: {e}\033[0m")