"""Background task for collecting telemetry data from MBTA API"""
import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Vehicle, TelemetryEvent
from services.mbta_client import MBTAClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Major MBTA routes to track
MAJOR_ROUTES = "Red,Orange,Green,Blue"


class TelemetryCollector:
    """Collects telemetry data from MBTA API every 30 seconds"""
    
    def __init__(self):
        self.client = MBTAClient()
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    async def collect_telemetry(self):
        """Collect telemetry data from MBTA API and store in database"""
        try:
            logger.info("Starting telemetry collection...")
            
            # Fetch vehicle data from MBTA API
            api_response = await self.client.get_vehicles(route_filter=MAJOR_ROUTES)
            
            if not api_response:
                logger.warning("No data received from MBTA API")
                return
            
            # Parse vehicle data
            vehicles_data = self.client.parse_vehicle_data(api_response)
            
            if not vehicles_data:
                logger.warning("No vehicles parsed from API response")
                return
            
            logger.info(f"Collected {len(vehicles_data)} vehicles")
            
            # Store in database with bulk operations
            db: Session = SessionLocal()
            try:
                collection_time = datetime.utcnow()
                
                # Get existing vehicles for efficient lookup
                existing_vehicle_ids = {v.vehicle_id: v for v in db.query(Vehicle).all()}
                
                # Prepare bulk updates and inserts
                vehicles_to_update = []
                vehicles_to_insert = []
                telemetry_events = []
                
                for vehicle_data in vehicles_data:
                    vehicle_id = vehicle_data['vehicle_id']
                    
                    if vehicle_id in existing_vehicle_ids:
                        # Update existing record
                        existing = existing_vehicle_ids[vehicle_id]
                        existing.route_id = vehicle_data.get('route_id')
                        existing.route_name = vehicle_data.get('route_name')
                        existing.latitude = vehicle_data.get('latitude')
                        existing.longitude = vehicle_data.get('longitude')
                        existing.bearing = vehicle_data.get('bearing')
                        existing.speed = vehicle_data.get('speed')
                        existing.current_status = vehicle_data.get('current_status')
                        existing.last_updated = collection_time
                        vehicles_to_update.append(existing)
                    else:
                        # Create new record
                        new_vehicle = Vehicle(
                            vehicle_id=vehicle_id,
                            route_id=vehicle_data.get('route_id'),
                            route_name=vehicle_data.get('route_name'),
                            latitude=vehicle_data.get('latitude'),
                            longitude=vehicle_data.get('longitude'),
                            bearing=vehicle_data.get('bearing'),
                            speed=vehicle_data.get('speed'),
                            current_status=vehicle_data.get('current_status'),
                            last_updated=collection_time
                        )
                        vehicles_to_insert.append(new_vehicle)
                    
                    # Prepare telemetry event
                    telemetry_events.append(TelemetryEvent(
                        vehicle_id=vehicle_id,
                        route_id=vehicle_data.get('route_id'),
                        latitude=vehicle_data.get('latitude'),
                        longitude=vehicle_data.get('longitude'),
                        speed=vehicle_data.get('speed'),
                        current_status=vehicle_data.get('current_status'),
                        timestamp=collection_time
                    ))
                
                # Bulk insert new vehicles
                if vehicles_to_insert:
                    db.bulk_save_objects(vehicles_to_insert)
                
                # Bulk insert telemetry events
                if telemetry_events:
                    db.bulk_save_objects(telemetry_events)
                
                db.commit()
                logger.info(f"Successfully stored {len(vehicles_data)} vehicles ({len(vehicles_to_insert)} new, {len(vehicles_to_update)} updated) and {len(telemetry_events)} telemetry events")
                
            except Exception as e:
                logger.error(f"Error storing telemetry data: {str(e)}")
                db.rollback()
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error during telemetry collection: {str(e)}")
    
    def start(self):
        """Start the collector scheduler"""
        if self.is_running:
            logger.warning("Collector is already running")
            return
        
        # Schedule collection every 10 seconds for near real-time updates
        self.scheduler.add_job(
            self.collect_telemetry,
            'interval',
            seconds=10,
            id='telemetry_collection',
            max_instances=1,
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info("Telemetry collector started (10 second interval)")
    
    def stop(self):
        """Stop the collector scheduler"""
        if not self.is_running:
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Telemetry collector stopped")


# Global collector instance
collector = TelemetryCollector()


async def start_collector():
    """Start the telemetry collector"""
    collector.start()
    
    # Keep the event loop running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping collector...")
        collector.stop()


if __name__ == "__main__":
    asyncio.run(start_collector())
