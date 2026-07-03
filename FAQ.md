# FAQ and Troubleshooting

## Frequently Asked Questions

### General Questions

**Q: What is Wayfarer?**
A: Wayfarer is an AI-powered multi-agent travel concierge that helps users plan trips by coordinating specialized agents for flights, hotels, itineraries, and final travel plan synthesis.

**Q: Do I need an account to use Wayfarer?**
A: No account is required for basic usage. The system uses a session ID (default: "lalitsharma_user") to maintain conversation history within a browser session.

**Q: Is my travel data stored permanently?**
A: Conversation history is stored in PostgreSQL for the duration of your session. Generated travel plans can be downloaded as PDF or Markdown for permanent storage.

**Q: Can I use Wayfarer for business travel planning?**
A: Absolutely! Wayfarer is designed for both leisure and business travel planning.

### Technical Questions

**Q: What LLMs does Wayfarer use?**
A: Wayfarer primarily uses Groq's LLaMA 3.3 70B model for its language understanding and generation capabilities.

**Q: Where does the flight data come from?**
A: Flight data is sourced from the AviationStack API, providing real-time flight schedules and pricing information.

**Q: How does Wayfarer find hotel information?**
A: Hotel and local attraction information is gathered using the Tavily Search API, which provides comprehensive and up-to-date travel information.

**Q: Is an internet connection required?**
A: Yes, Wayfarer requires an internet connection to access external APIs for flight and hotel data, as well as to communicate with the LLM service.

### Usage Questions

**Q: How specific should my travel request be?**
A: The more details you provide (destination, dates, budget, preferences), the more personalized your travel plan will be. However, the system can work with vague requests and will ask for clarification when needed.

**Q: Can I modify an existing travel plan?**
A: Yes! Simply provide additional details or changes to your original request, and the system will update your plan accordingly.

**Q: How long does it take to generate a travel plan?**
A: Typical response time is 10-30 seconds, depending on the complexity of the request and API response times.

**Q: Can I save my travel plans for later?**
A: Yes, use the download buttons to save your plan as a PDF or Markdown file.

### Privacy and Security

**Q: Is my personal information secure?**
A: Wayfarer takes privacy seriously. API keys and sensitive data are stored in environment variables and never exposed to users.

**Q: What data is collected?**
A: Only the travel queries you input and the generated responses are stored temporarily in the database for session continuity.

**Q: How can I delete my data?**
A: Session data is temporary and cleared when the browser session ends. For immediate concerns, simply close the browser tab.

## Troubleshooting Guide

### Common Issues

**Problem: "Please describe your trip first" error appears**
- Solution: Make sure you've entered text in the trip description box before clicking "Generate My Travel Plan"

**Problem: Application is stuck on "Checking your request..."**
- Solution: This usually indicates a temporary API issue. Try refreshing the page and trying again after a moment.

**Problem: No flight or hotel results are shown**
- Solution: 
  1. Check that your destination is specified clearly
  2. Verify that the AviationStack and Tavily APIs are accessible
  3. Try a more popular or well-known destination
  4. Check your internet connection

**Problem: Error messages about API keys or authentication**
- Solution: This indicates a configuration issue. The API keys need to be properly set in the environment variables:
  - GROQ_API_KEY
  - AVIATIONSTACK_API_KEY  
  - TAVILY_API_KEY
  - DATABASE_URL

**Problem: PDF generation fails**
- Solution: 
  1. Ensure reportlab is installed (`pip install reportlab`)
  2. Check that the travel_plans directory is writable
  3. Try downloading the Markdown version instead

**Problem: Application runs slowly or times out**
- Solution:
  1. Clear your browser cache and try again
  2. Check your internet connection speed
  3. Try during off-peak hours if experiencing API rate limits
  4. Consider simplifying your request (e.g., shorter trip duration)

### Technical Deployment Issues

**Problem: Streamlit fails to start**
- Solution:
  1. Verify Python version (3.8+ recommended)
  2. Check that all dependencies are installed: `pip install -r requirements.txt`
  3. Ensure port 8501 is available or change the port in `.streamlit/config.toml`

**Problem: Database connection errors**
- Solution:
  1. Verify DATABASE_URL is correctly formatted
  2. Check that your PostgreSQL instance is accessible
  3. Ensure SSL mode is correctly configured if required
  4. Test the connection independently with a PSQL client

**Problem: Module import errors**
- Solution:
  1. Ensure you're in the project root directory
  2. Check that all required packages are installed
  3. Try reinstalling: `pip install --upgrade -r requirements.txt`
  4. Verify Python path includes the project directory

### Getting Help

If you continue to experience issues:
1. Check the console/error logs for specific error messages
2. Verify all environment variables are set correctly
3. Ensure you have a stable internet connection
4. Try simplifying your request to isolate the problem
5. Consult the API documentation for service-specific limitations
6. Consider reaching out to support with:
   - Exact error message
   - Steps to reproduce the issue
   - Browser and version information
   - Time and date when the issue occurred

## Known Limitations

### API Rate Limits
- AviationStack: Free tier has monthly request limits
- Tavily: Usage limits apply based on subscription tier
- Groq: Rate limits based on your plan

### Geographic Coverage
- Flight data coverage depends on AviationStack's partnerships
- Hotel information availability varies by location and popularity
- Some remote or newly developed locations may have limited information

### Language Support
- Currently optimized for English-language queries
- Some international destination names may require English spelling

### Temporal Constraints
- Real-time flight data is subject to change
- Hotel availability and pricing are dynamic
- Recommendations are based on currently available data

## Version History

### v1.0.0 (Initial Release)
- Core multi-agent architecture
- Streamlit-based UI with visual agent tracking
- Flight, hotel, and itinerary agents
- PDF and Markdown export capabilities
- PostgreSQL conversation persistence

### Planned Features
- User accounts and saved preferences
- Interactive map integration
- Real-time price tracking
- Collaborative trip planning
- Travel budget forecasting
- Integration with calendar applications