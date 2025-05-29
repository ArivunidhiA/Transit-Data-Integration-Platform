import aiohttp
import asyncio
import logging
import ssl
import certifi
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from src.database.models import Vehicle, Trip, Alert, Route, Stop
from config.settings import (
    MBTA_API_KEY, VEHICLES_ENDPOINT, PREDICTIONS_ENDPOINT,
    ALERTS_ENDPOINT, ROUTES_ENDPOINT, STOPS_ENDPOINT,
    DATABASE_URL, COLLECTION_INTERVAL, MAX_RETRIES, RETRY_DELAY
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MbtACollector:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.session = Session(self.engine)
        self.headers = {'x-api-key': MBTA_API_KEY}
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        
    async def fetch_data(self, endpoint, params=None):
        """Fetch data from MBTA API with retry logic"""
        for attempt in range(MAX_RETRIES):
            try:
                connector = aiohttp.TCPConnector(ssl=self.ssl_context)
                async with aiohttp.ClientSession(headers=self.headers, connector=connector) as session:
                    async with session.get(endpoint, params=params) as response:
                        if response.status == 200:
                            return await response.json()
                        else:
                            error_text = await response.text()
                            logger.error(f"API request failed: {response.status} - {error_text}")
                            if response.status == 400:
                                logger.error(f"Request URL: {endpoint}")
                                logger.error(f"Request params: {params}")
                                logger.error(f"Request headers: {self.headers}")
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY)
        return None

    async def collect_vehicles(self):
        """Collect vehicle positions for all routes"""
        routes = self.session.query(Route).all()
        for route in routes:
            params = {"filter[route]": route.id}
            data = await self.fetch_data(VEHICLES_ENDPOINT, params=params)
            logger.info(f"Fetched vehicles for route {route.id}: {data}")
            if data and 'data' in data:
                try:
                    for vehicle in data['data']:
                        attrs = vehicle['attributes']
                        rels = vehicle.get('relationships', {})
                        route_id = rels.get('route', {}).get('data', {}).get('id') or route.id
                        trip_id = rels.get('trip', {}).get('data', {}).get('id')
                        logger.info(f"Parsed vehicle: id={vehicle['id']}, route_id={route_id}, trip_id={trip_id}, timestamp={attrs.get('timestamp')}")
                        vehicle_obj = Vehicle(
                            id=vehicle['id'],
                            route_id=route_id,
                            trip_id=trip_id,
                            latitude=attrs.get('latitude'),
                            longitude=attrs.get('longitude'),
                            bearing=attrs.get('bearing'),
                            speed=attrs.get('speed'),
                            status=attrs.get('status'),
                            current_stop=attrs.get('current_stop'),
                            next_stop=attrs.get('next_stop'),
                            timestamp=datetime.fromisoformat(attrs.get('updated_at')) if attrs.get('updated_at') else None
                        )
                        self.session.merge(vehicle_obj)
                    self.session.commit()
                except Exception as e:
                    logger.error(f"Error processing vehicle data: {str(e)}")
                    self.session.rollback()

    async def collect_trips(self):
        """Collect trip updates for all routes"""
        routes = self.session.query(Route).all()
        for route in routes:
            params = {"filter[route]": route.id}
            data = await self.fetch_data(PREDICTIONS_ENDPOINT, params=params)
            logger.info(f"Fetched trips for route {route.id}: {data}")
            if data and 'data' in data:
                for trip in data['data']:
                    attrs = trip['attributes']
                    rels = trip.get('relationships', {})
                    trip_id = rels.get('trip', {}).get('data', {}).get('id') or trip.get('id')
                    route_id = rels.get('route', {}).get('data', {}).get('id') or route.id
                    vehicle_id = rels.get('vehicle', {}).get('data', {}).get('id')
                    # Use arrival_time and departure_time as start/end
                    start_time = attrs.get('departure_time') or attrs.get('arrival_time')
                    end_time = attrs.get('arrival_time') or attrs.get('departure_time')
                    logger.info(f"Parsed trip: trip_id={trip_id}, route_id={route_id}, vehicle_id={vehicle_id}, start_time={start_time}, end_time={end_time}, status={attrs.get('status')}")
                    trip_obj = Trip(
                        id=trip_id,
                        route_id=route_id,
                        schedule_relationship=attrs.get('schedule_relationship'),
                        vehicle_id=vehicle_id,
                        start_time=datetime.fromisoformat(start_time) if start_time else None,
                        end_time=datetime.fromisoformat(end_time) if end_time else None,
                        status=attrs.get('status')
                    )
                    self.session.merge(trip_obj)
                self.session.commit()

    async def collect_alerts(self):
        """Collect service alerts for all routes"""
        routes = self.session.query(Route).all()
        for route in routes:
            params = {"filter[route]": route.id}
            data = await self.fetch_data(ALERTS_ENDPOINT, params=params)
            if data and 'data' in data:
                for alert in data['data']:
                    attrs = alert['attributes']
                    alert_obj = Alert(
                        id=alert['id'],
                        header_text=attrs.get('header_text'),
                        description_text=attrs.get('description_text'),
                        effect=attrs.get('effect'),
                        severity=attrs.get('severity'),
                        created_at=datetime.fromisoformat(attrs.get('created_at')) if attrs.get('created_at') else None,
                        updated_at=datetime.fromisoformat(attrs.get('updated_at')) if attrs.get('updated_at') else None,
                        active_period_start=datetime.fromisoformat(attrs.get('active_period_start')) if attrs.get('active_period_start') else None,
                        active_period_end=datetime.fromisoformat(attrs.get('active_period_end')) if attrs.get('active_period_end') else None,
                        route_id=attrs.get('route_id')
                    )
                    self.session.merge(alert_obj)
                self.session.commit()

    async def collect_routes(self):
        """Collect route information"""
        data = await self.fetch_data(ROUTES_ENDPOINT)
        if data and 'data' in data:
            for route in data['data']:
                attrs = route['attributes']
                route_obj = Route(
                    id=route['id'],
                    name=attrs.get('long_name') or attrs.get('short_name') or attrs.get('name'),
                    type=attrs.get('type'),
                    description=attrs.get('description'),
                    color=attrs.get('color'),
                    text_color=attrs.get('text_color')
                )
                self.session.merge(route_obj)
            self.session.commit()

    async def collect_stops(self):
        """Collect stop information for all routes"""
        routes = self.session.query(Route).all()
        for route in routes:
            params = {"filter[route]": route.id}
            data = await self.fetch_data(STOPS_ENDPOINT, params=params)
            if data and 'data' in data:
                try:
                    for stop in data['data']:
                        attrs = stop['attributes']
                        stop_obj = Stop(
                            id=stop['id'],
                            name=attrs.get('name'),
                            latitude=attrs.get('latitude'),
                            longitude=attrs.get('longitude'),
                            wheelchair_boarding=attrs.get('wheelchair_boarding'),
                            platform_code=attrs.get('platform_code')
                        )
                        self.session.merge(stop_obj)
                    self.session.commit()
                except Exception as e:
                    logger.error(f"Error processing stop data: {str(e)}")
                    self.session.rollback()

    async def collect_all(self):
        """Collect all data types and update route metrics"""
        tasks = [
            self.collect_vehicles(),
            self.collect_trips(),
            self.collect_alerts(),
            self.collect_routes(),
            self.collect_stops()
        ]
        await asyncio.gather(*tasks)

        # Calculate and save metrics for each route
        from src.analytics.route_analyzer import RouteAnalyzer
        analyzer = RouteAnalyzer()
        routes = self.session.query(Route).all()
        for route in routes:
            try:
                analyzer.calculate_route_metrics(route.id)
            except Exception as e:
                logger.error(f"Error calculating metrics for route {route.id}: {str(e)}")

    async def run(self):
        """Run the collector continuously"""
        while True:
            try:
                await self.collect_all()
                logger.info("Data collection completed successfully")
            except Exception as e:
                logger.error(f"Error during data collection: {str(e)}")
            await asyncio.sleep(COLLECTION_INTERVAL) 