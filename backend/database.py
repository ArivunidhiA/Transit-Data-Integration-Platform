"""Database models and initialization for MBTA Telemetry Platform"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class Vehicle(Base):
    """Current state of vehicles (real-time)"""
    __tablename__ = 'vehicles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(String, unique=True, nullable=False)
    route_id = Column(String)
    route_name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    bearing = Column(Integer)
    speed = Column(Float)
    current_status = Column(String)  # STOPPED_AT, IN_TRANSIT_TO, INCOMING_AT
    last_updated = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_route', 'route_id'),
        Index('idx_updated', 'last_updated'),
    )


class TelemetryEvent(Base):
    """Time-series historical telemetry data"""
    __tablename__ = 'telemetry_events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    vehicle_id = Column(String, nullable=False)
    route_id = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)
    current_status = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_vehicle_time', 'vehicle_id', 'timestamp'),
        Index('idx_route_time', 'route_id', 'timestamp'),
    )


class RouteDelay(Base):
    """Aggregated delay metrics by route and hour"""
    __tablename__ = 'route_delays'

    id = Column(Integer, primary_key=True, autoincrement=True)
    route_id = Column(String, nullable=False)
    route_name = Column(String)
    hour_of_day = Column(Integer)
    avg_delay_minutes = Column(Float)
    sample_count = Column(Integer)
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_route_hour', 'route_id', 'hour_of_day'),
    )


# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./data/mbta_telemetry.db')

# Ensure data directory exists
db_path = DATABASE_URL.replace('sqlite:///', './')
db_dir = os.path.dirname(db_path) if os.path.dirname(db_path) else './data'
os.makedirs(db_dir, exist_ok=True)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
