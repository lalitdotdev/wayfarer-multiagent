# Wayfarer - Multi-Agent Travel Concierge

## Overview
Wayfarer is an intelligent multi-agent travel planning system that uses LangGraph to coordinate specialized agents for flights, hotels, itineraries, and final travel plan synthesis. The system provides a beautiful Streamlit interface for users to plan their trips with AI-powered recommendations.

## Features

- **Multi-Agent Architecture**: Specialized agents for flight search, hotel search, itinerary creation, and final plan synthesis
- **Real-time Streaming**: Watch agents work in parallel with live updates in the Streamlit interface
- **Beautiful UI**: Custom Streamlit interface with animations, visual feedback, and boarding pass-style results
- **Memory Persistence**: PostgreSQL-backed checkpointing for conversation history and session persistence
- **Export Options**: Generate and download travel plans as Markdown or PDF files
- **Multi-LLM Support**: Powered by Groq's LLaMA 3.3 70B model for fast, high-quality responses
- **External APIs**: Integrated with Tavily for search and AviationStack for flight data
- **Extensible Design**: Modular architecture makes it easy to add new agents or capabilities

## Architecture

```
User Query → Router Agent → [Flight Agent, Hotel Agent] (Parallel) → Itinerary Agent → Final Agent → User Response
                                                       ↑
                                                Planner Agent ← Chitchat Agent
```

### Agents

1. **Router Agent**: Determines if query is travel-related or chitchat
2. **Planner Agent**: Extracts travel details (destination, dates, etc.) from user query
3. **Flight Agent**: Searches for flight options using AviationStack API
4. **Hotel Agent**: Finds hotel options using Tavily search
5. **Itinerary Agent**: Creates personalized travel itinerary from flight/hotel data
6. **Final Agent**: Synthesizes all information into a beautiful final response
7. **Chitchat Agent**: Handles general conversation and guides back to travel planning

## Technology Stack

- **Framework**: LangGraph for stateful multi-agent workflows
- **LLM**: Groq (LLaMA 3.3 70B) for fast inference
- **Frontend**: Streamlit for interactive web interface
- **Search**: Tavily API for hotel and travel information search
- **Flight Data**: AviationStack API for real-time flight information
- **Database**: PostgreSQL with PostgresSaver for checkpointing
- **PDF Generation**: ReportLab for travel plan exports
- **Environment**: Python 3.8+

## Installation

### Option 1: Automated Setup (Recommended)
For a quick and easy setup, use the provided setup script:
```bash
# Clone the repository
git clone https://github.com/yourusername/wayfarer.git
cd wayfarer

# Run the setup script (handles virtual environment, dependencies, and configuration)
chmod +x setup.sh
./setup.sh

# Activate the environment (if not already activated)
source venv/bin/activate
```

### Option 2: Manual Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/wayfarer.git
   cd wayfarer
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys:
   GROQ_API_KEY="your_groq_api_key_here"
   AVIATIONSTACK_API_KEY="your_aviationstack_api_key_here"
   TAVILY_API_KEY="your_tavily_api_key_here"
   DATABASE_URL="postgresql://user:password@host:5432/database_name"
   ```

5. Run the application:
   ```bash
   streamlit run app.py
   ```

## Quick Start (Using Docker)
For the fastest way to try Wayfarer locally:
```bash
# Clone the repository
git clone https://github.com/yourusername/wayfarer.git
cd wayfarer

# Create a .env file with your API keys
cp .env.example .env
# Edit .env with your actual API keys

# Build and run with Docker
docker build -t wayfarer .
docker run -p 8501:8501 --env-file .env wayfarer
```
Then open your browser to http://localhost:8501

## Usage

1. Enter your Passenger ID (optional, for conversation memory)
2. Describe your trip in the text area (e.g., "Plan a 7-day Japan trip under ₹2 lakhs")
3. Click "Generate My Travel Plan"
4. Watch the agents work in real-time with visual feedback
5. View your personalized travel plan in the boarding pass format
6. Download as Markdown or PDF for offline use

## Testing

Run the test suite with pytest:

```bash
# Install test dependencies (if not already in requirements)
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=./ --cov-report=html
```

To run specific test modules:

```bash
pytest tests/test_integration.py
pytest tests/test_router_agent.py
```

## Deployment

### Streamlit Community Cloud (Recommended for Demo)

1. Fork the repository on GitHub
2. Sign in to [Streamlit Community Cloud](https://streamlit.io/cloud)
3. Click "New app"
4. Select your repository
5. Set main file path: `app.py`
6. Add environment variables in secrets:
   ```toml
   [secrets]
   GROQ_API_KEY = "your_key_here"
   AVIATIONSTACK_API_KEY = "your_key_here"
   TAVILY_API_KEY = "your_key_here"
   DATABASE_URL = "your_postgres_url_here"
   ```
7. Click "Deploy"

### Docker Deployment

```bash
# Build the image
docker build -t wayfarer .

# Run the container
docker run -p 8501:8501 \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  -e AVIATIONSTACK_API_KEY=$AVIATIONSTACK_API_KEY \
  -e TAVILY_API_KEY=$TAVILY_API_KEY \
  -e DATABASE_URL=$DATABASE_URL \
  wayfarer
```

### Traditional Server/VPS

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables (see above)
3. Run: `streamlit run app.py --server.port=8501 --server.address=0.0.0.0`

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

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | API key for Groq LLM | Yes |
| `AVIATIONSTACK_API_KEY` | API key for AviationStack flight data | Yes |
| `TAVILY_API_KEY` | API key for Tavily search | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |

## API Documentation

See [API_DOCS.md](API_DOCS.md) for detailed API documentation of the internal modules.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines on how to contribute to Wayfarer.

## License

MIT License - feel free to use and modify for personal or commercial projects.

## Acknowledgments

- LangGraph team for the excellent multi-agent framework
- Groq for fast LLM inference
- Streamlit for the beautiful frontend framework
- Tavily and AviationStack for their travel APIs
- ReportLab for PDF generation capabilities
EOF