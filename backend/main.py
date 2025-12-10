"""FastAPI application for MBTA Telemetry Platform"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
from typing import List, Optional
import os
import logging

from database import get_db, init_db, Vehicle, TelemetryEvent, RouteDelay
from collector import collector
from services.delay_calculator import DelayCalculator
from services.alert_detector import AlertDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MBTA Transit Telemetry Platform",
    description="Real-time telemetry collection and observability platform for MBTA transit vehicles",
    version="1.0.0"
)

# CORS configuration
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and start collector on startup"""
    logger.info("Initializing database...")
    init_db()
    
    # Start telemetry collector
    logger.info("Starting telemetry collector...")
    collector.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Stop collector on shutdown"""
    logger.info("Stopping telemetry collector...")
    collector.stop()


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    
    Returns 200 if system is healthy, 503 if not
    """
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        
        # Check last collection time
        last_vehicle = db.query(Vehicle).order_by(Vehicle.last_updated.desc()).first()
        last_collection = last_vehicle.last_updated if last_vehicle else None
        
        # Check if last collection was within last 2 minutes
        is_recent = False
        if last_collection:
            time_diff = datetime.utcnow() - last_collection
            is_recent = time_diff < timedelta(minutes=2)
        
        # Count tracked vehicles
        vehicle_count = db.query(func.count(Vehicle.id)).scalar() or 0
        
        # Calculate uptime (simplified - would track actual start time in production)
        uptime_seconds = 0
        if last_vehicle:
            # Approximate uptime from first collection
            first_collection = db.query(func.min(TelemetryEvent.timestamp)).scalar()
            if first_collection:
                uptime_seconds = int((datetime.utcnow() - first_collection).total_seconds())
        
        if not is_recent and last_collection:
            return {
                "status": "unhealthy",
                "message": "Last collection was more than 2 minutes ago",
                "database": "connected",
                "last_collection": last_collection.isoformat(),
                "uptime_seconds": uptime_seconds,
                "vehicles_tracked": vehicle_count
            }, 503
        
        return {
            "status": "healthy",
            "database": "connected",
            "last_collection": last_collection.isoformat() if last_collection else None,
            "uptime_seconds": uptime_seconds,
            "vehicles_tracked": vehicle_count
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }, 503


@app.get("/vehicles")
async def get_vehicles(
    route_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get current vehicle positions
    
    Args:
        route_id: Optional filter by route ID
    
    Returns:
        List of current vehicle positions
    """
    query = db.query(Vehicle)
    
    if route_id:
        query = query.filter(Vehicle.route_id == route_id)
    
    # Only return vehicles updated in last 2 minutes (optimized for faster queries)
    cutoff = datetime.utcnow() - timedelta(minutes=2)
    vehicles = query.filter(
        Vehicle.last_updated >= cutoff
    ).order_by(Vehicle.last_updated.desc()).all()  # Order by most recent for consistency
    
    return [
        {
            "id": v.id,
            "vehicle_id": v.vehicle_id,
            "route_id": v.route_id,
            "route_name": v.route_name,
            "latitude": v.latitude,
            "longitude": v.longitude,
            "bearing": v.bearing,
            "speed": v.speed,
            "current_status": v.current_status,
            "last_updated": v.last_updated.isoformat()
        }
        for v in vehicles
    ]


@app.get("/routes/{route_id}/delays")
async def get_route_delays(
    route_id: str,
    hours: int = 24,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Get delay history for a route
    
    Args:
        route_id: Route identifier
        hours: Number of hours to look back (default 24)
        background_tasks: For triggering delay calculation
    
    Returns:
        Delay history with average delays by hour
    """
    # Trigger delay calculation in background if needed
    calculator = DelayCalculator(db)
    
    # Get existing delay history
    delay_history = calculator.get_delay_history(route_id, hours_back=hours)
    
    # If no recent delays, calculate them
    if not delay_history:
        try:
            calculator.calculate_route_delays(route_id, hours_back=hours)
            delay_history = calculator.get_delay_history(route_id, hours_back=hours)
        except Exception as e:
            logger.error(f"Error calculating delays: {str(e)}")
    
    return {
        "route_id": route_id,
        "hours_back": hours,
        "delays": delay_history
    }


@app.get("/analytics/headway")
async def get_headway_analysis(
    route_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get headway analysis (time between consecutive vehicles)
    
    Args:
        route_id: Optional filter by route
    
    Returns:
        Headway statistics
    """
    query = db.query(TelemetryEvent)
    
    if route_id:
        query = query.filter(TelemetryEvent.route_id == route_id)
    
    # Get events from last hour
    cutoff = datetime.utcnow() - timedelta(hours=1)
    events = query.filter(
        TelemetryEvent.timestamp >= cutoff
    ).order_by(TelemetryEvent.route_id, TelemetryEvent.timestamp).all()
    
    # Group by route and vehicle to calculate headways
    headways_by_route = {}
    
    current_route = None
    current_vehicle = None
    last_timestamp = None
    
    for event in events:
        if event.route_id != current_route:
            current_route = event.route_id
            current_vehicle = None
            last_timestamp = None
            if current_route not in headways_by_route:
                headways_by_route[current_route] = []
        
        if event.vehicle_id != current_vehicle:
            current_vehicle = event.vehicle_id
            last_timestamp = event.timestamp
            continue
        
        if last_timestamp:
            headway_seconds = (event.timestamp - last_timestamp).total_seconds()
            headways_by_route[current_route].append(headway_seconds / 60)  # Convert to minutes
            last_timestamp = event.timestamp
    
    # Calculate statistics
    result = {}
    for route_id, headways in headways_by_route.items():
        if headways:
            result[route_id] = {
                "count": len(headways),
                "avg_minutes": sum(headways) / len(headways),
                "min_minutes": min(headways),
                "max_minutes": max(headways),
                "headways": headways[:100]  # Limit to first 100 for response size
            }
    
    return {
        "route_id": route_id,
        "analysis": result
    }


@app.get("/analytics/system")
async def get_system_analytics(db: Session = Depends(get_db)):
    """
    Get system-wide analytics and metrics
    
    Returns:
        System statistics including total events, routes, etc.
    """
    # Count total telemetry events
    total_events = db.query(func.count(TelemetryEvent.id)).scalar() or 0
    
    # Count unique routes
    unique_routes = db.query(func.count(func.distinct(Vehicle.route_id))).scalar() or 0
    
    # Count current vehicles
    current_vehicles = db.query(func.count(Vehicle.id)).scalar() or 0
    
    # Get recent events count (last hour)
    cutoff = datetime.utcnow() - timedelta(hours=1)
    recent_events = db.query(func.count(TelemetryEvent.id)).filter(
        TelemetryEvent.timestamp >= cutoff
    ).scalar() or 0
    
    # Calculate data points per second
    events_per_second = recent_events / 3600 if recent_events > 0 else 0
    
    return {
        "total_telemetry_events": total_events,
        "routes_monitored": unique_routes,
        "vehicles_tracked": current_vehicles,
        "events_last_hour": recent_events,
        "events_per_second": round(events_per_second, 2),
        "collection_frequency_seconds": 30
    }


@app.get("/metrics")
async def get_metrics(db: Session = Depends(get_db)):
    """
    Prometheus-compatible metrics endpoint for monitoring
    
    Returns:
        System metrics in a structured format
    """
    # Collection success metrics (would track over time in production)
    total_events = db.query(func.count(TelemetryEvent.id)).scalar() or 0
    
    # Recent collection rate
    cutoff_5min = datetime.utcnow() - timedelta(minutes=5)
    events_5min = db.query(func.count(TelemetryEvent.id)).filter(
        TelemetryEvent.timestamp >= cutoff_5min
    ).scalar() or 0
    
    # Vehicles per route
    vehicles_per_route = {}
    routes = db.query(Vehicle.route_id, func.count(Vehicle.id)).group_by(Vehicle.route_id).all()
    for route_id, count in routes:
        if route_id:
            vehicles_per_route[route_id] = count
    
    # Database size estimate (SQLite specific)
    import os
    db_size = 0
    try:
        db_path = os.getenv('DATABASE_URL', 'sqlite:///./data/mbta_telemetry.db').replace('sqlite:///', './')
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path)
    except:
        pass
    
    return {
        "telemetry_events_total": total_events,
        "telemetry_events_per_minute": events_5min / 5,
        "vehicles_tracked": db.query(func.count(Vehicle.id)).scalar() or 0,
        "routes_monitored": len(vehicles_per_route),
        "vehicles_per_route": vehicles_per_route,
        "database_size_bytes": db_size,
        "collection_interval_seconds": 30,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/alerts")
async def get_alerts(
    route_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get system alerts and anomalies
    
    Args:
        route_id: Optional route filter
    
    Returns:
        List of active alerts
    """
    detector = AlertDetector(db)
    alerts = detector.get_all_alerts(route_id)
    
    # Sort by severity and timestamp
    severity_order = {'warning': 1, 'info': 2, 'error': 0}
    alerts.sort(key=lambda x: (severity_order.get(x.get('severity', 'info'), 2), x.get('timestamp', '')))
    
    return {
        "count": len(alerts),
        "alerts": alerts,
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
