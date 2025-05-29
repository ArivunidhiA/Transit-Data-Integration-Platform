import os
from sqlalchemy import create_engine
from src.database.models import Base
from config.settings import DATABASE_URL

def init_database():
    """Initialize the database with all tables"""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database() 