# flight_tool.py
import os
import logging
import requests
from typing import Optional
from dotenv import load_dotenv
from tools.tavily_tool import tavily_search

load_dotenv()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def search_flights(query: str, dep_iata: Optional[str] = None, arr_iata: Optional[str] = None) -> str:
    """
    Search for flights. Attempts to use AviationStack if a key and parameters are available,
    otherwise falls back to a real-time web search via Tavily.

    Args:
        query: The search query string
        dep_iata: Optional departure IATA code
        arr_iata: Optional arrival IATA code

    Returns:
        Formatted flight information string
    """
    # 1. Try AviationStack API if parameters and API key are available
    if API_KEY and (dep_iata or arr_iata):
        try:
            url = "http://api.aviationstack.com/v1/flights"
            params = {
                "access_key": API_KEY,
                "limit": 10  # Increased limit for better results
            }
            if dep_iata:
                params["dep_iata"] = dep_iata.upper()  # Ensure uppercase
            if arr_iata:
                params["arr_iata"] = arr_iata.upper()  # Ensure uppercase

            logger.info(f"Calling AviationStack API with params: {params}")
            # Added timeout and better error handling
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # Raises HTTPError for bad responses

            data = response.json()
            if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
                flights = []
                for flight in data["data"][:10]:  # Limit to 10 results
                    # Safely extract nested data with defaults
                    airline_info = flight.get("airline", {}) or {}
                    departure_info = flight.get("departure", {}) or {}
                    arrival_info = flight.get("arrival", {}) or {}

                    airline = airline_info.get("name", "Unknown Airline")
                    departure = departure_info.get("airport", "Unknown Airport")
                    arrival = arrival_info.get("airport", "Unknown Airport")
                    status = flight.get("flight_status", "scheduled")
                    flight_date = flight.get("flight_date", "N/A")

                    # Format departure and arrival times if available
                    dep_time = departure_info.get("estimated", "") or departure_info.get("scheduled", "")
                    arr_time = arrival_info.get("estimated", "") or arrival_info.get("scheduled", "")

                    flight_info = f"Airline: {airline} | Departure: {departure}"
                    if dep_time:
                        flight_info += f" ({dep_time})"
                    flight_info += f" | Arrival: {arrival}"
                    if arr_time:
                        flight_info += f" ({arr_time})"
                    flight_info += f" | Status: {status} | Date: {flight_date}"

                    flights.append(flight_info)

                logger.info(f"AviationStack API returned {len(flights)} flights")
                return "\n".join(flights)
            else:
                logger.warning("AviationStack API returned no flight data")
        except requests.exceptions.Timeout:
            logger.error("AviationStack API request timed out")
        except requests.exceptions.RequestException as e:
            logger.error(f"AviationStack API request failed: {e}")
        except ValueError as e:
            logger.error(f"Failed to parse AviationStack API response: {e}")
        except Exception as e:
            logger.error(f"Unexpected error calling AviationStack API: {e}")
            # Fall through to Tavily if API fails

    # 2. Fallback: Search using Tavily for real-time web results
    try:
        # Clean up the query parameters for better search
        dep_part = f"from {dep_iata}" if dep_iata else ""
        arr_part = f"to {arr_iata}" if arr_iata else ""
        search_query = f"flights {dep_part} {arr_part} {query}".strip()
        # Remove extra spaces
        search_query = " ".join(search_query.split())

        logger.info(f"Falling back to Tavily search with query: {search_query}")
        tavily_results = tavily_search(search_query)
        if tavily_results and "error" not in tavily_results.lower():
            logger.info("Tavily search returned results")
            return tavily_results
        else:
            logger.warning("Tavily search returned no useful results")
    except Exception as e:
        logger.error(f"Error during Tavily search fallback: {e}")

    logger.warning("All flight search methods failed")
    return "Unable to retrieve flight information at this time. Please check your connection and try again later."