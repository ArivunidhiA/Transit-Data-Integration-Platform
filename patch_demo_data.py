import json
from datetime import datetime, timedelta
from random import uniform

# Load routes
with open('routes.json') as f:
    routes = json.load(f)

# Load vehicles
with open('vehicles.json') as f:
    vehicles = json.load(f)

# Load trips
with open('trips.json') as f:
    trips = json.load(f)

# Always generate new route_metrics for demo
route_metrics = []

now = datetime.utcnow()

# Patch vehicles: ensure every route has at least 10 demo vehicles with timestamps spread over 24 hours
for route in routes:
    route_id = route['id']
    route_vehicles = [v for v in vehicles if v['route_id'] == route_id]
    for i in range(10 - len(route_vehicles)):
        vehicles.append({
            'id': f'demo_vehicle_{route_id}_{i}',
            'route_id': route_id,
            'trip_id': f'demo_trip_{route_id}_{i}',
            'latitude': 42.35 + 0.01 * i,
            'longitude': -71.06 - 0.01 * i,
            'bearing': 90.0,
            'speed': 20.0,
            'timestamp': (now - timedelta(hours=24 - i*2)).isoformat(),
            'status': 'IN_TRANSIT',
            'current_stop': None,
            'next_stop': None
        })
    for i, v in enumerate([v for v in vehicles if v['route_id'] == route_id and v['id'].startswith('demo_vehicle_')]):
        v['timestamp'] = (now - timedelta(hours=24 - i*2)).isoformat()

# Patch trips: ensure every route has at least 10 demo trips with start and end times spread over 24 hours
for route in routes:
    route_id = route['id']
    route_trips = [t for t in trips if t['route_id'] == route_id and t['start_time'] and t['end_time']]
    for i in range(10 - len(route_trips)):
        start = now - timedelta(hours=24 - i*2)
        end = start + timedelta(minutes=10)
        trips.append({
            'id': f'demo_trip_{route_id}_{i}',
            'route_id': route_id,
            'schedule_relationship': None,
            'vehicle_id': f'demo_vehicle_{route_id}_{i}',
            'start_time': start.isoformat(),
            'end_time': end.isoformat(),
            'status': 'COMPLETED'
        })
    for i, t in enumerate([t for t in trips if t['route_id'] == route_id and t['id'].startswith('demo_trip_')]):
        start = now - timedelta(hours=24 - i*2)
        end = start + timedelta(minutes=10)
        t['start_time'] = start.isoformat()
        t['end_time'] = end.isoformat()

# Always generate 10 random route_metrics per route
for route in routes:
    route_id = route['id']
    for i in range(10):
        ts = now - timedelta(hours=24 - i*2)
        route_metrics.append({
            'id': None,
            'route_id': route_id,
            'timestamp': ts.isoformat(),
            'average_delay': round(uniform(0.5, 5), 2),
            'headway_variance': round(uniform(1000, 100000), 2),
            'bunching_score': round(uniform(0.1, 1), 2),
            'completion_rate': round(uniform(0.5, 1.0), 2)
        })

with open('vehicles_demo.json', 'w') as f:
    json.dump(vehicles, f, indent=2)
with open('trips_demo.json', 'w') as f:
    json.dump(trips, f, indent=2)
with open('route_metrics_demo.json', 'w') as f:
    json.dump(route_metrics, f, indent=2)
print('Patched vehicles_demo.json, trips_demo.json, and route_metrics_demo.json with random demo data for all routes (10 points over 24 hours).') 