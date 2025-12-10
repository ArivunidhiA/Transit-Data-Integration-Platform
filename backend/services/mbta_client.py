"""MBTA API client for fetching vehicle telemetry data"""
import httpx
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

MBTA_API_KEY = os.getenv('MBTA_API_KEY')
MBTA_BASE_URL = 'https://api-v3.mbta.com'
VEHICLES_ENDPOINT = f"{MBTA_BASE_URL}/vehicles"


class MBTAClient:
    """Client for interacting with MBTA API"""
    
    def __init__(self):
        self.api_key = MBTA_API_KEY
        self.base_url = MBTA_BASE_URL
        self.headers = {'x-api-key': self.api_key} if self.api_key else {}
    
    async def get_vehicles(self, route_filter: Optional[str] = None, retries: int = 3) -> Dict[str, Any]:
        """
        Fetch vehicle data from MBTA API with retry logic and exponential backoff
        
        Args:
            route_filter: Comma-separated route IDs (e.g., "Red,Orange,Green,Blue")
            retries: Number of retry attempts
        
        Returns:
            API response JSON or None if error
        """
        import asyncio
        
        params = {
            'include': 'trip,route',
            'fields[vehicle]': 'current_status,bearing,latitude,longitude,speed,updated_at'
        }
        
        if route_filter:
            params['filter[route]'] = route_filter
        
        for attempt in range(retries):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        VEHICLES_ENDPOINT,
                        params=params,
                        headers=self.headers
                    )
                    
                    # Handle rate limiting with exponential backoff
                    if response.status_code == 429:
                        wait_time = (2 ** attempt) * 5  # Exponential backoff: 5s, 10s, 20s
                        logger.warning(f"Rate limited. Waiting {wait_time}s before retry {attempt + 1}/{retries}")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    response.raise_for_status()
                    return response.json()
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < retries - 1:
                    # Retry on server errors
                    wait_time = (2 ** attempt) * 2
                    logger.warning(f"Server error {e.response.status_code}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error(f"MBTA API error: {e.response.status_code} - {e.response.text}")
                    return None
            except httpx.TimeoutException:
                if attempt < retries - 1:
                    wait_time = (2 ** attempt) * 2
                    logger.warning(f"Request timeout. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                else:
                    logger.error("Request timeout after all retries")
                    return None
            except Exception as e:
                logger.error(f"Error fetching vehicles from MBTA API: {str(e)}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return None
        
        return None
    
    def parse_vehicle_data(self, api_response: Dict[str, Any]) -> list:
        """
        Parse MBTA API response into structured vehicle data
        
        Returns:
            List of vehicle dictionaries
        """
        if not api_response or 'data' not in api_response:
            return []
        
        vehicles = []
        included_routes = {}
        
        # Build route lookup from included data
        if 'included' in api_response:
            for item in api_response['included']:
                if item.get('type') == 'route':
                    included_routes[item['id']] = item['attributes'].get('long_name') or item['attributes'].get('short_name', item['id'])
        
        for vehicle_item in api_response['data']:
            attrs = vehicle_item.get('attributes', {})
            rels = vehicle_item.get('relationships', {})
            
            route_id = None
            route_name = None
            if 'route' in rels and 'data' in rels['route']:
                route_id = rels['route']['data'].get('id')
                route_name = included_routes.get(route_id, route_id)
            
            vehicle = {
                'vehicle_id': vehicle_item['id'],
                'route_id': route_id,
                'route_name': route_name,
                'latitude': attrs.get('latitude'),
                'longitude': attrs.get('longitude'),
                'bearing': attrs.get('bearing'),
                'speed': attrs.get('speed'),
                'current_status': attrs.get('current_status'),
                'updated_at': attrs.get('updated_at')
            }
            vehicles.append(vehicle)
        
        return vehicles
