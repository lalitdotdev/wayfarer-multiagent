# Wayfarer - Multi-Agent Travel Concierge

## Overview
Wayfarer is an intelligent multi-agent travel planning system that uses LangGraph to coordinate specialized agents for flights, hotels, itineraries, and final travel plan synthesis. The system provides a beautiful Streamlit interface for users to plan their trips with AI-powered recommendations.

## Features
- **Multi-Agent Architecture**: Specialized agents for flight search, hotel search, itinerary creation, and final plan synthesis
- **Real-time Streaming**: Watch agents work in parallel with live updates
- **Beautiful UI**: Custom Streamlit interface with animations and visual feedback
- **Memory Persistence**: PostgreSQL-backed checkpointing for conversation history
- **Export Options**: Generate and download travel plans as Markdown or PDF
- **Multi-LLM Support**: Powered by Groq's LLaMA 3.3 70B model
- **External APIs**: Integrated with Tavily for search and AviationStack for flight data

## Architecture
```
User Query → Router Agent → [Flight Agent, Hotel Agent] (Parallel) → Itinerary Agent → Final Agent → User Response
                                                        ↑
                                                Planner Agent ← Chitchat Agent
```

## Agents
1. **Router Agent**: Determines if query is travel-related or chitchat
2. **Planner Agent**: Extracts travel details (destination, dates, etc.) from user query
3. **Flight Agent**: Searches for flight options using AviationStack API
4. **Hotel Agent**: Finds hotel options using Tavily search
5. **Itinerary Agent**: Creates personalized travel itinerary from flight/hotel data
6. **Final Agent**: Synthesizes all information into a beautiful final response
7. **Chitchat Agent**: Handles general conversation and guides back to travel planning

## Technology Stack
- **Framework**: LangGraph for stateful multi-agent workflows
- **LLM**: Groq (LLaMA 3.3 70B)
- **Frontend**: Streamlit
- **Search**: Tavily API
- **Flight Data**: AviationStack API
- **Database**: PostgreSQL with PostgresSaver for checkpointing
- **PDF Generation**: ReportLab
- **Environment**: Python 3.8+

## Installation
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env`:
   - `GROQ_API_KEY`: For LLM access
   - `AVIATIONSTACK_API_KEY`: For flight data
   - `TAVILY_API_KEY`: For hotel/search data
   - `DATABASE_URL`: PostgreSQL connection string
4. Run the application: `streamlit run app.py`

## Usage
1. Enter your Passenger ID (optional, for conversation memory)
2. Describe your trip in the text area (e.g., "Plan a 7-day Japan trip under ₹2 lakhs")
3. Click "Generate My Travel Plan"
4. Watch the agents work in real-time
5. View your personalized travel plan in the boarding pass format
6. Download as Markdown or PDF for offline use

## Deployment
The application can be deployed to any platform that supports Streamlit and Python:
- Streamlit Community Cloud
- Docker containers
- Traditional VPS/cloud servers
- Platform-as-a-service (Heroku, Render, etc.)

## Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | API key for Groq LLM | Yes |
| `AVIATIONSTACK_API_KEY` | API key for AviationStack flight data | Yes |
| `TAVILY_API_KEY` | API key for Tavily search | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |

## Project Structure
```
.
├── app.py              # Streamlit frontend
├── main.py             # LangGraph multi-agent workflow
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (not in git)
├── .gitignore          # Git ignore rules
├── travel_plans/       # Generated travel plans (auto-saved)
├── tools/              # Custom tool implementations
│   ├── flight_tool.py  # Flight search functionality
│   ├── tavily_tool.py  # Tavily search wrapper
│   └── __init__.py
├── langgraph-env3/     # Virtual environment
├── __pycache__/        # Python cache
├── .streamlit/         # Streamlit configuration
└── scratch/            # Temporary files
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## License
MIT License - feel free to use and modify for personal or commercial projects.

## Acknowledgments
- LangGraph team for the excellent multi-agent framework
- Groq for fast LLM inference
- Streamlit for the beautiful frontend framework
- Tavily and AviationStack for their travel APIs