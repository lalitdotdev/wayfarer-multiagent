# Deployment Guide for Wayfarer

This document provides instructions for deploying the Wayfarer travel concierge application to various platforms.

## Prerequisites
- Python 3.8+
- PostgreSQL database
- API keys for:
  - Groq (LLM)
  - AviationStack (flight data)
  - Tavior (search)

## Deployment Options

### 1. Streamlit Community Cloud (Recommended for Demo)
1. Fork/repository on GitHub
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

### 2. Docker Deployment
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

### 3. Traditional Server/VPS
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables:
   ```bash
   export GROQ_API_KEY="your_key"
   export AVIATIONSTACK_API_KEY="your_key"
   export TAVILY_API_KEY="your_key"
   export DATABASE_URL="your_postgres_url"
   ```
3. Run the application:
   ```bash
   streamlit run app.py --server.port=8501 --server.address=0.0.0.0
   ```

### 4. Kubernetes
See `kubernetes/` directory for manifests.

## Environment Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `GROQ_API_KEY` | Groq API key for LLM | `gsk_...` |
| `AVIATIONSTACK_API_KEY` | AviationStack API key | `your_key_here` |
| `TAVILY_API_KEY` | Tavily API key | `tvly-dev-...` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host:5432/db` |

## Performance Optimization
- Use connection pooling for database
- Enable Streamlit caching where appropriate
- Consider using a CDN for static assets
- Monitor API rate limits

## Monitoring & Logging
- Streamlit provides built-in logging
- Consider adding health check endpoints
- Monitor API usage and costs
- Set up error tracking (Sentry, etc.)

## Security Considerations
- Never commit `.env` file to version control
- Use environment variables for secrets
- Keep dependencies updated
- Consider adding rate limiting for public deployments
- Use HTTPS in production

## Troubleshooting
### Common Issues
1. **Database connection failed**
   - Verify DATABASE_URL is correct
   - Ensure PostgreSQL instance is accessible
   - Check SSL settings if required

2. **API key errors**
   - Verify keys are valid and have sufficient quota
   - Check for trailing spaces in environment variables

3. **Module import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

4. **Streamlit port already in use**
   - Change port: `streamlit run app.py --server.port=8502`
   - Or kill existing process on port 8501

## Scaling Recommendations
For high-traffic deployments:
1. Use a process manager like Gunicorn with multiple workers
2. Implement caching layer (Redis) for frequent queries
3. Consider separating frontend and backend services
4. Use load balancer for horizontal scaling
5. Implement request queuing for API calls to external services

## Backup & Recovery
1. Regularly backup PostgreSQL database
2. Export/import travel plans from `travel_plans/` directory if needed
3. Document recovery procedures
4. Test backup restoration periodically

## Version Updates
To update the application:
1. Pull latest changes: `git pull origin main`
2. Update dependencies: `pip install -r requirements.txt`
3. Restart the application
4. Check for any breaking changes in dependencies