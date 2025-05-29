import uvicorn
from app import app
from config.settings import DASHBOARD_HOST, DASHBOARD_PORT

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=DASHBOARD_HOST,
        port=DASHBOARD_PORT,
        reload=True
    ) 