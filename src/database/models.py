from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Vehicle(Base):
    __tablename__ = 'vehicles'
    
    id = Column(String, primary_key=True)
    route_id = Column(String)
    trip_id = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    bearing = Column(Float)
    speed = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String)
    current_stop = Column(String)
    next_stop = Column(String)

class Trip(Base):
    __tablename__ = 'trips'
    
    id = Column(String, primary_key=True)
    route_id = Column(String)
    schedule_relationship = Column(String)
    vehicle_id = Column(String, ForeignKey('vehicles.id'))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(String)
    
    vehicle = relationship("Vehicle")

class Route(Base):
    __tablename__ = 'routes'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    type = Column(String)
    description = Column(String)
    color = Column(String)
    text_color = Column(String)

class Stop(Base):
    __tablename__ = 'stops'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    wheelchair_boarding = Column(Integer)
    platform_code = Column(String)

class Alert(Base):
    __tablename__ = 'alerts'
    
    id = Column(String, primary_key=True)
    header_text = Column(String)
    description_text = Column(String)
    effect = Column(String)
    severity = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    active_period_start = Column(DateTime)
    active_period_end = Column(DateTime)
    route_id = Column(String, ForeignKey('routes.id'))
    
    route = relationship("Route")

class RouteMetrics(Base):
    __tablename__ = 'route_metrics'
    
    id = Column(Integer, primary_key=True)
    route_id = Column(String, ForeignKey('routes.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    average_delay = Column(Float)
    headway_variance = Column(Float)
    bunching_score = Column(Float)
    completion_rate = Column(Float)
    
    route = relationship("Route") 