"""Service for detecting anomalies and generating alerts"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from database import Vehicle, TelemetryEvent
import logging

logger = logging.getLogger(__name__)

# Alert thresholds
DELAY_THRESHOLD_MINUTES = 5
BUNCHING_THRESHOLD_SECONDS = 180  # 3 minutes between vehicles
SPEED_ANOMALY_THRESHOLD = 60  # mph (unusual for transit)

class AlertDetector:
    """Detect anomalies in transit data"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def detect_bunching(self, route_id: str) -> list:
        """
        Detect vehicle bunching (vehicles too close together)
        
        Returns:
            List of alerts with vehicle pairs that are bunched
        """
        alerts = []
        
        # Get recent vehicle positions for route
        cutoff = datetime.utcnow() - timedelta(minutes=5)
        vehicles = self.db.query(Vehicle).filter(
            Vehicle.route_id == route_id,
            Vehicle.last_updated >= cutoff,
            Vehicle.latitude.isnot(None),
            Vehicle.longitude.isnot(None)
        ).order_by(Vehicle.last_updated).all()
        
        # Check consecutive vehicles on same route
        for i in range(len(vehicles) - 1):
            v1 = vehicles[i]
            v2 = vehicles[i + 1]
            
            # Simple distance check (in a real system, would use proper geospatial calculations)
            if v1.latitude and v2.latitude and v1.longitude and v2.longitude:
                # Approximate distance (simplified)
                time_diff = (v2.last_updated - v1.last_updated).total_seconds()
                if 0 < time_diff < BUNCHING_THRESHOLD_SECONDS:
                    alerts.append({
                        'type': 'bunching',
                        'route_id': route_id,
                        'vehicle_1': v1.vehicle_id,
                        'vehicle_2': v2.vehicle_id,
                        'time_between_seconds': time_diff,
                        'severity': 'warning',
                        'timestamp': datetime.utcnow().isoformat()
                    })
        
        return alerts
    
    def detect_speed_anomalies(self, route_id: str) -> list:
        """
        Detect unusual speeds (too fast or stopped too long)
        
        Returns:
            List of speed anomaly alerts
        """
        alerts = []
        
        cutoff = datetime.utcnow() - timedelta(minutes=5)
        vehicles = self.db.query(Vehicle).filter(
            Vehicle.route_id == route_id,
            Vehicle.last_updated >= cutoff,
            Vehicle.speed.isnot(None)
        ).all()
        
        for vehicle in vehicles:
            if vehicle.speed is not None:
                if vehicle.speed > SPEED_ANOMALY_THRESHOLD:
                    alerts.append({
                        'type': 'speed_anomaly',
                        'route_id': route_id,
                        'vehicle_id': vehicle.vehicle_id,
                        'speed': vehicle.speed,
                        'severity': 'warning',
                        'timestamp': datetime.utcnow().isoformat()
                    })
        
        return alerts
    
    def detect_stalled_vehicles(self) -> list:
        """
        Detect vehicles that haven't moved in a while
        
        Returns:
            List of stalled vehicle alerts
        """
        alerts = []
        
        # Get vehicles that haven't updated position in 10 minutes
        cutoff = datetime.utcnow() - timedelta(minutes=10)
        stalled = self.db.query(Vehicle).filter(
            Vehicle.last_updated < cutoff,
            Vehicle.current_status == 'IN_TRANSIT_TO'
        ).all()
        
        for vehicle in stalled:
            alerts.append({
                'type': 'stalled',
                'route_id': vehicle.route_id,
                'vehicle_id': vehicle.vehicle_id,
                'last_update': vehicle.last_updated.isoformat(),
                'severity': 'info',
                'timestamp': datetime.utcnow().isoformat()
            })
        
        return alerts
    
    def get_all_alerts(self, route_id: str = None) -> list:
        """
        Get all alerts for a route or system-wide
        
        Args:
            route_id: Optional route filter
        
        Returns:
            List of all alerts
        """
        all_alerts = []
        
        if route_id:
            routes = [route_id]
        else:
            # Get all routes with active vehicles
            routes = [r[0] for r in self.db.query(Vehicle.route_id).distinct().all() if r[0]]
        
        for route in routes:
            all_alerts.extend(self.detect_bunching(route))
            all_alerts.extend(self.detect_speed_anomalies(route))
        
        # Add stalled vehicles (system-wide)
        all_alerts.extend(self.detect_stalled_vehicles())
        
        return all_alerts
