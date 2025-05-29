import os
import subprocess
import sys
import time
from pathlib import Path

def check_environment():
    """Check if all required environment variables are set"""
    if not os.getenv('MBTA_API_KEY'):
        print("Error: MBTA_API_KEY environment variable is not set")
        print("Please set it in your .env file")
        sys.exit(1)

def initialize_database():
    """Initialize the SQLite database"""
    print("Initializing database...")
    subprocess.run([sys.executable, "src/database/init_db.py"], check=True)

def start_collector():
    """Start the data collector in a separate process"""
    print("Starting data collector...")
    return subprocess.Popen([sys.executable, "src/collectors/main.py"])

def start_dashboard():
    """Start the dashboard in a separate process"""
    print("Starting dashboard...")
    return subprocess.Popen([sys.executable, "src/dashboard/main.py"])

def main():
    # Check environment
    check_environment()
    
    # Create necessary directories
    Path("data").mkdir(exist_ok=True)
    Path("src/dashboard/static").mkdir(exist_ok=True)
    Path("src/dashboard/templates").mkdir(exist_ok=True)
    
    # Initialize database
    initialize_database()
    
    # Start services
    collector_process = start_collector()
    dashboard_process = start_dashboard()
    
    print("\nServices started successfully!")
    print("Dashboard available at: http://localhost:8000")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Keep the main process running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down services...")
        collector_process.terminate()
        dashboard_process.terminate()
        print("Services stopped")

if __name__ == "__main__":
    main() 