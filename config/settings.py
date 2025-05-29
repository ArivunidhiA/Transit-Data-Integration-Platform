import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
MBTA_API_KEY = os.getenv('MBTA_API_KEY')
MBTA_API_BASE_URL = 'https://api-v3.mbta.com'

# API Endpoints
VEHICLES_ENDPOINT = f"{MBTA_API_BASE_URL}/vehicles"
PREDICTIONS_ENDPOINT = f"{MBTA_API_BASE_URL}/predictions"
ALERTS_ENDPOINT = f"{MBTA_API_BASE_URL}/alerts"
ROUTES_ENDPOINT = f"{MBTA_API_BASE_URL}/routes"
STOPS_ENDPOINT = f"{MBTA_API_BASE_URL}/stops"

# Data Collection Settings
COLLECTION_INTERVAL = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Database Settings
DATABASE_URL = 'sqlite:///data/mbta_transit.db'

# Analysis Settings
BUNCHING_THRESHOLD = 300  # seconds (5 minutes)
HEADWAY_VARIANCE_THRESHOLD = 0.3  # 30% variance
DELAY_THRESHOLD = 300  # seconds (5 minutes)

# Dashboard Settings
DASHBOARD_HOST = '0.0.0.0'
DASHBOARD_PORT = 8000
REFRESH_INTERVAL = 60  # seconds 