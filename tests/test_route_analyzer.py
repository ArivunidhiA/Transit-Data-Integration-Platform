import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from database.models import Base, Route, RouteMetrics, Vehicle, Trip
from analytics.route_analyzer import RouteAnalyzer
from config.settings import DATABASE_URL

@pytest.fixture
def test_db():
    """Create a test database"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def session(test_db):
    """Create a test session"""
    return Session(test_db)

@pytest.fixture
def analyzer(session):
    """Create a route analyzer instance"""
    return RouteAnalyzer()

def test_calculate_average_delay(analyzer, session):
    """Test average delay calculation"""
    # Create test data
    route = Route(id='test-route', name='Test Route')
    session.add(route)
    
    trip = Trip(
        id='test-trip',
        route_id='test-route',
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow() + timedelta(minutes=30),
        status='COMPLETED'
    )
    session.add(trip)
    
    # Add vehicle positions
    for i in range(3):
        vehicle = Vehicle(
            id=f'vehicle-{i}',
            route_id='test-route',
            trip_id='test-trip',
            timestamp=datetime.utcnow() + timedelta(minutes=i*10)
        )
        session.add(vehicle)
    
    session.commit()
    
    # Calculate delay
    delay = analyzer.calculate_average_delay('test-route')
    assert isinstance(delay, float)
    assert delay >= 0

def test_calculate_headway_variance(analyzer, session):
    """Test headway variance calculation"""
    # Create test data
    route = Route(id='test-route', name='Test Route')
    session.add(route)
    
    # Add vehicle positions with known intervals
    for i in range(5):
        vehicle = Vehicle(
            id=f'vehicle-{i}',
            route_id='test-route',
            timestamp=datetime.utcnow() + timedelta(minutes=i*10)
        )
        session.add(vehicle)
    
    session.commit()
    
    # Calculate variance
    variance = analyzer.calculate_headway_variance('test-route')
    assert isinstance(variance, float)
    assert variance >= 0

def test_detect_bunching(analyzer, session):
    """Test bunching detection"""
    # Create test data
    route = Route(id='test-route', name='Test Route')
    session.add(route)
    
    # Add vehicle positions with some bunching
    timestamps = [
        datetime.utcnow(),
        datetime.utcnow() + timedelta(minutes=2),  # Bunching
        datetime.utcnow() + timedelta(minutes=15),
        datetime.utcnow() + timedelta(minutes=17),  # Bunching
        datetime.utcnow() + timedelta(minutes=30)
    ]
    
    for i, ts in enumerate(timestamps):
        vehicle = Vehicle(
            id=f'vehicle-{i}',
            route_id='test-route',
            timestamp=ts
        )
        session.add(vehicle)
    
    session.commit()
    
    # Calculate bunching score
    score = analyzer.detect_bunching('test-route')
    assert isinstance(score, float)
    assert 0 <= score <= 1

def test_calculate_completion_rate(analyzer, session):
    """Test completion rate calculation"""
    # Create test data
    route = Route(id='test-route', name='Test Route')
    session.add(route)
    
    # Add trips with different statuses
    statuses = ['COMPLETED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED']
    for i, status in enumerate(statuses):
        trip = Trip(
            id=f'trip-{i}',
            route_id='test-route',
            status=status,
            start_time=datetime.utcnow() - timedelta(minutes=30)
        )
        session.add(trip)
    
    session.commit()
    
    # Calculate completion rate
    rate = analyzer.calculate_completion_rate('test-route')
    assert isinstance(rate, float)
    assert 0 <= rate <= 1
    assert rate == 0.5  # 2 completed out of 4 trips 