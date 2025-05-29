from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from src.database.models import Route, RouteMetrics, Vehicle, Trip
from src.analytics.route_analyzer import RouteAnalyzer
from config.settings import DATABASE_URL

app = FastAPI(title="MBTA Transit Analytics Dashboard")

# Initialize database connection
engine = create_engine(DATABASE_URL)
session = sessionmaker(engine)()
analyzer = RouteAnalyzer()

# Mount static files
app.mount("/static", StaticFiles(directory="src/dashboard/static"), name="static")

# Templates
templates = Jinja2Templates(directory="src/dashboard/templates")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    routes = session.query(Route).all()
    # Use the latest route_metrics for each route
    route_metrics = {}
    for route in routes:
        metric = session.query(RouteMetrics).filter(RouteMetrics.route_id == route.id).order_by(RouteMetrics.timestamp.desc()).first()
        if metric:
            route_metrics[route.id] = {
                'name': route.name,
                'efficiency_score': 100 * metric.completion_rate if metric.completion_rate is not None else 0,
                'average_delay': metric.average_delay,
                'headway_variance': metric.headway_variance,
                'bunching_score': metric.bunching_score,
                'completion_rate': metric.completion_rate
            }
        else:
            route_metrics[route.id] = {
                'name': route.name,
                'efficiency_score': 0,
                'average_delay': 0,
                'headway_variance': 0,
                'bunching_score': 0,
                'completion_rate': 0
            }
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "routes": routes,
            "route_metrics": route_metrics
        }
    )

@app.get("/api/routes")
async def get_routes():
    """Get all routes with their metrics"""
    routes = session.query(Route).all()
    result = {}
    for route in routes:
        metric = session.query(RouteMetrics).filter(RouteMetrics.route_id == route.id).order_by(RouteMetrics.timestamp.desc()).first()
        result[route.id] = {
            'name': route.name,
            'efficiency_score': 100 * metric.completion_rate if metric and metric.completion_rate is not None else 0
        }
    return result

@app.get("/api/route/{route_id}/metrics")
async def get_route_metrics(route_id: str):
    """Get detailed metrics for a specific route"""
    metric = session.query(RouteMetrics).filter(RouteMetrics.route_id == route_id).order_by(RouteMetrics.timestamp.desc()).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Route metrics not found")
    return {
        "route_id": route_id,
        "timestamp": metric.timestamp,
        "average_delay": metric.average_delay,
        "headway_variance": metric.headway_variance,
        "bunching_score": metric.bunching_score,
        "completion_rate": metric.completion_rate
    }

@app.get("/api/route/{route_id}/vehicles")
async def get_route_vehicles(route_id: str):
    """Get current vehicle positions for a route"""
    vehicles = session.query(Vehicle).filter(
        Vehicle.route_id == route_id,
        Vehicle.timestamp >= datetime.utcnow() - timedelta(minutes=5)
    ).all()
    
    return [
        {
            "id": v.id,
            "latitude": v.latitude,
            "longitude": v.longitude,
            "bearing": v.bearing,
            "speed": v.speed,
            "status": v.status,
            "current_stop": v.current_stop,
            "next_stop": v.next_stop
        }
        for v in vehicles
    ]

@app.get("/api/route/{route_id}/delays")
async def get_route_delays(route_id: str):
    """Get delay history for a route"""
    metrics = session.query(RouteMetrics).filter(
        RouteMetrics.route_id == route_id
    ).order_by(RouteMetrics.timestamp).all()
    return [
        {
            "timestamp": m.timestamp,
            "average_delay": m.average_delay
        }
        for m in metrics
    ]

@app.get("/api/route/{route_id}/bunching")
async def get_route_bunching(route_id: str):
    """Get bunching history for a route"""
    metrics = session.query(RouteMetrics).filter(
        RouteMetrics.route_id == route_id
    ).order_by(RouteMetrics.timestamp).all()
    return [
        {
            "timestamp": m.timestamp,
            "bunching_score": m.bunching_score
        }
        for m in metrics
    ]

@app.get("/api/route/{route_id}/completion")
async def get_route_completion(route_id: str):
    """Get completion rate history for a route"""
    metrics = session.query(RouteMetrics).filter(
        RouteMetrics.route_id == route_id
    ).order_by(RouteMetrics.timestamp).all()
    return [
        {
            "timestamp": m.timestamp,
            "completion_rate": m.completion_rate
        }
        for m in metrics
    ] 