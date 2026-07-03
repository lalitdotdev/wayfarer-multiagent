# flight_tool.py
import os
import logging
import requests
from dotenv import load_dotenv
from tools.tavily_tool import tavily_search

load_dotenv()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def search_flights(query: str, dep_iata: str = None, arr_iata: str = None) -> str:
    """
    Search for flights. Attempts to use AviationStack if a key and parameters are available,
    otherwise falls back to a real-time web search via Tavily.
    """
    # 1. Try AviationStack API if parameters and API key are available
    if API_KEY and (dep_iata or arr_iata):
        try:
            url = "http://api.aviationstack.com/v1/flights"
            params = {
                "access_key": API_KEY,
                "limit": 5
            }
            if dep_iata:
                params["dep_iata"] = dep_iata
            if arr_iata:
                params["arr_iata"] = arr_iata

            logger.info(f"Calling AviationStack API with params: {params}")
            response = requests.get(url, params=params, timeout=8)
            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    flights = []
                    for flight in data["data"][:5]:
                        airline = flight.get("airline", {}).get("name", "Unknown Airline")
                        departure = flight.get("departure", {}).get("airport", "Unknown Airport")
                        arrival = flight.get("arrival", {}).get("airport", "Unknown Airport")
                        status = flight.get("flight_status", "scheduled")
                        flight_date = flight.get("flight_date", "N/A")

                        flights.append(
                            f"Airline: {airline} | Departure: {departure} | Arrival: {arrival} | Status: {status} | Date: {flight_date}"
                        )
                    logger.info(f"AviationStack API returned {len(flights)} flights")
                    return "\n".join(flights)
                else:
                    logger.warning("AviationStack API returned no flight data")
            else:
                logger.warning(f"AviationStack API returned status code: {response.status_code}")
        except Exception as e:
            logger.error(f"Error calling AviationStack API: {e}")
            # Fall through to Tavily if API fails

    # 2. Fallback: Search using Tavily for real-time web results
    search_query = f"flights options routes flights from {dep_iata or ''} to {arr_iata or ''} {query}".strip()
    logger.info(f"Falling back to Tavily search with query: {search_query}")
    try:
        tavily_results = tavily_search(search_query)
        if tavily_results:
            logger.info("Tavily search returned results")
            return tavily_results
    except Exception as e:
        logger.error(f"Error during Tavily search fallback: {e}")

    logger.warning("All flight search methods failed")
    return "No live flight data retrieved. Please verify the destination and departure cities."