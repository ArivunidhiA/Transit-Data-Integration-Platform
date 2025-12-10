# Quick Start Guide

Get the MBTA Transit Telemetry Platform running locally in 5 minutes.

## Prerequisites

- Python 3.11+
- Node.js 18+
- MBTA API key ([Get one here](https://api-v3.mbta.com/register))

## Backend Setup (2 minutes)

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export MBTA_API_KEY=your_api_key_here
# Or create .env file: echo "MBTA_API_KEY=your_api_key_here" > .env

# Initialize database
python init_db.py

# Start the backend server
uvicorn main:app --reload
```

Backend will run at `http://localhost:8000`

## Frontend Setup (2 minutes)

```bash
# Navigate to frontend (in a new terminal)
cd frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env

# Start the frontend
npm run dev
```

Frontend will run at `http://localhost:3000`

## Verify It's Working

1. Open `http://localhost:3000` in your browser
2. Check the Overview page - you should see system status
3. Wait 30 seconds for the first data collection
4. Check the Live Map page - vehicles should appear on the map

## Troubleshooting

**Backend won't start:**
- Make sure Python 3.11+ is installed: `python --version`
- Verify MBTA_API_KEY is set: `echo $MBTA_API_KEY`
- Check database directory exists: `ls -la backend/data/`

**Frontend won't start:**
- Make sure Node.js 18+ is installed: `node --version`
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`
- Check VITE_API_URL is set: `cat .env`

**No data showing:**
- Wait at least 30 seconds for first collection
- Check backend logs for errors
- Verify MBTA API key is valid
- Check browser console for API errors

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Explore the API docs at `http://localhost:8000/docs`
