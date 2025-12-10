"""Service for calculating route delays from telemetry data"""
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta
from database import TelemetryEvent, RouteDelay
import logging

logger = logging.getLogger(__name__)

# Scheduled headways in minutes (example - adjust based on actual MBTA schedules)
SCHEDULED_HEADWAYS = {
    'Red': 6,
    'Orange': 6,
    'Green': 5,
    'Blue': 7,
    '1': 10,
    '39': 8,
    # Add more routes as needed
}


class DelayCalculator:
    """Calculate delays and route metrics from telemetry events"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_route_delays(self, route_id: str, hours_back: int = 24) -> None:
        """
        Calculate average delays by hour of day for a route
        
        Args:
            route_id: Route identifier
            hours_back: Number of hours to look back for calculation
        """
        try:
            # Get telemetry events for this route within time window
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            
            events = self.db.query(TelemetryEvent).filter(
                TelemetryEvent.route_id == route_id,
                TelemetryEvent.timestamp >= cutoff_time
            ).order_by(TelemetryEvent.timestamp).all()
            
            if not events:
                logger.info(f"No events found for route {route_id}")
                return
            
            # Get route name from first event or use route_id
            route_name = events[0].route_id if events else route_id
            
            # Group events by hour of day and calculate delays
            delays_by_hour = {}
            
            # Get scheduled headway for this route
            scheduled_headway = SCHEDULED_HEADWAYS.get(route_id, 10)  # Default 10 minutes
            
            # Group events by vehicle and hour
            vehicles_by_hour = {}
            for event in events:
                hour = event.timestamp.hour
                vehicle_id = event.vehicle_id
                
                if hour not in vehicles_by_hour:
                    vehicles_by_hour[hour] = {}
                if vehicle_id not in vehicles_by_hour[hour]:
                    vehicles_by_hour[hour][vehicle_id] = []
                
                vehicles_by_hour[hour][vehicle_id].append(event)
            
            # Calculate delays for each hour
            for hour, vehicles in vehicles_by_hour.items():
                delays = []
                
                for vehicle_id, vehicle_events in vehicles.items():
                    if len(vehicle_events) < 2:
                        continue
                    
                    # Calculate actual headway between consecutive events
                    for i in range(1, len(vehicle_events)):
                        time_diff = (vehicle_events[i].timestamp - vehicle_events[i-1].timestamp).total_seconds() / 60
                        # Delay = actual headway - scheduled headway
                        delay = time_diff - scheduled_headway
                        delays.append(delay)
                
                if delays:
                    avg_delay = sum(delays) / len(delays)
                    
                    # Update or create route_delay record
                    existing = self.db.query(RouteDelay).filter(
                        RouteDelay.route_id == route_id,
                        RouteDelay.hour_of_day == hour
                    ).first()
                    
                    if existing:
                        existing.avg_delay_minutes = avg_delay
                        existing.sample_count = len(delays)
                        existing.calculated_at = datetime.utcnow()
                    else:
                        route_delay = RouteDelay(
                            route_id=route_id,
                            route_name=route_name,
                            hour_of_day=hour,
                            avg_delay_minutes=avg_delay,
                            sample_count=len(delays)
                        )
                        self.db.add(route_delay)
            
            self.db.commit()
            logger.info(f"Calculated delays for route {route_id}")
            
        except Exception as e:
            logger.error(f"Error calculating delays for route {route_id}: {str(e)}")
            self.db.rollback()
            raise
    
    def get_delay_history(self, route_id: str, hours_back: int = 24) -> list:
        """
        Get delay history for a route
        
        Returns:
            List of delay records with hour and average delay
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        delays = self.db.query(RouteDelay).filter(
            RouteDelay.route_id == route_id,
            RouteDelay.calculated_at >= cutoff_time
        ).order_by(RouteDelay.hour_of_day).all()
        
        return [
            {
                'hour_of_day': d.hour_of_day,
                'avg_delay_minutes': d.avg_delay_minutes,
                'sample_count': d.sample_count,
                'calculated_at': d.calculated_at.isoformat()
            }
            for d in delays
        ]
