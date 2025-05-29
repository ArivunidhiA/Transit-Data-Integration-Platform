import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from src.database.models import Route, Trip, Vehicle, RouteMetrics
from config.settings import (
    DATABASE_URL, BUNCHING_THRESHOLD,
    HEADWAY_VARIANCE_THRESHOLD, DELAY_THRESHOLD
)

class RouteAnalyzer:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.session = sessionmaker(self.engine)()

    def calculate_average_delay(self, route_id, time_window=3600):
        """Calculate average delay for a route (use all data for demo)"""
        trips = self.session.query(Trip).filter(
            Trip.route_id == route_id
        ).all()
        if not trips:
            return 0
        delays = []
        for trip in trips:
            if trip.start_time and trip.end_time:
                scheduled_duration = (trip.end_time - trip.start_time).total_seconds()
                actual_duration = scheduled_duration  # Use prediction as actual for now
                delay = actual_duration - scheduled_duration
                delays.append(delay)
        return np.mean(delays) if delays else 0

    def calculate_headway_variance(self, route_id, time_window=3600):
        """Calculate headway variance for a route (use all data for demo)"""
        vehicles = self.session.query(Vehicle).filter(
            Vehicle.route_id == route_id
        ).order_by(Vehicle.timestamp).all()
        if len(vehicles) < 2:
            return 0
        timestamps = [v.timestamp for v in vehicles]
        headways = np.diff([t.timestamp() for t in timestamps])
        return np.var(headways) if len(headways) > 0 else 0

    def detect_bunching(self, route_id, time_window=3600):
        """Detect vehicle bunching on a route (use all data for demo)"""
        vehicles = self.session.query(Vehicle).filter(
            Vehicle.route_id == route_id
        ).order_by(Vehicle.timestamp).all()
        if len(vehicles) < 2:
            return 0
        timestamps = [v.timestamp for v in vehicles]
        headways = np.diff([t.timestamp() for t in timestamps])
        bunching_count = sum(1 for h in headways if h < BUNCHING_THRESHOLD)
        return bunching_count / len(headways) if len(headways) > 0 else 0

    def calculate_completion_rate(self, route_id, time_window=3600):
        """Calculate route completion rate as ratio of trips with both start and end times (use all data for demo)"""
        trips = self.session.query(Trip).filter(
            Trip.route_id == route_id
        ).all()
        if not trips:
            return 0
        completed_trips = sum(1 for trip in trips if trip.start_time and trip.end_time)
        return completed_trips / len(trips)

    def _get_actual_duration(self, trip):
        """Get actual duration of a trip based on vehicle positions"""
        vehicle_positions = self.session.query(Vehicle).filter(
            Vehicle.trip_id == trip.id
        ).order_by(Vehicle.timestamp).all()
        
        if len(vehicle_positions) < 2:
            return None
        
        start_time = vehicle_positions[0].timestamp
        end_time = vehicle_positions[-1].timestamp
        return (end_time - start_time).total_seconds()

    def calculate_route_metrics(self, route_id):
        """Calculate all metrics for a route"""
        metrics = RouteMetrics(
            route_id=route_id,
            timestamp=datetime.utcnow(),
            average_delay=self.calculate_average_delay(route_id),
            headway_variance=self.calculate_headway_variance(route_id),
            bunching_score=self.detect_bunching(route_id),
            completion_rate=self.calculate_completion_rate(route_id)
        )
        
        self.session.add(metrics)
        self.session.commit()
        return metrics

    def get_route_efficiency_score(self, route_id):
        """Calculate overall route efficiency score"""
        metrics = self.calculate_route_metrics(route_id)
        
        # Normalize metrics to 0-1 scale
        delay_score = 1 - min(metrics.average_delay / DELAY_THRESHOLD, 1)
        headway_score = 1 - min(metrics.headway_variance / HEADWAY_VARIANCE_THRESHOLD, 1)
        bunching_score = 1 - metrics.bunching_score
        
        # Weighted average of all metrics
        efficiency_score = (
            0.3 * delay_score +
            0.3 * headway_score +
            0.2 * bunching_score +
            0.2 * metrics.completion_rate
        )
        
        return efficiency_score * 100  # Convert to percentage

    def get_all_route_metrics(self):
        """Get metrics for all routes"""
        routes = self.session.query(Route).all()
        return {
            route.id: {
                'name': route.name,
                'efficiency_score': self.get_route_efficiency_score(route.id)
            }
            for route in routes
        } 