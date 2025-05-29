import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Vehicle, Trip, RouteMetrics
from config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL)
session = sessionmaker(engine)()

def parse_datetime(val):
    if val is None:
        return None
    try:
        return datetime.fromisoformat(val)
    except Exception:
        return None

# Clear existing data
session.query(Vehicle).delete()
session.query(Trip).delete()
session.query(RouteMetrics).delete()
session.commit()

# Load and import vehicles
with open('vehicles_demo.json') as f:
    vehicles = json.load(f)
for v in vehicles:
    v = v.copy()
    if 'timestamp' in v:
        v['timestamp'] = parse_datetime(v['timestamp'])
    vehicle = Vehicle(**{k: v[k] for k in Vehicle.__table__.columns.keys() if k in v})
    session.merge(vehicle)
session.commit()
print(f"Imported {len(vehicles)} vehicles.")

# Load and import trips
with open('trips_demo.json') as f:
    trips = json.load(f)
for t in trips:
    t = t.copy()
    if 'start_time' in t:
        t['start_time'] = parse_datetime(t['start_time'])
    if 'end_time' in t:
        t['end_time'] = parse_datetime(t['end_time'])
    trip = Trip(**{k: t[k] for k in Trip.__table__.columns.keys() if k in t})
    session.merge(trip)
session.commit()
print(f"Imported {len(trips)} trips.")

# Load and import route_metrics
with open('route_metrics_demo.json') as f:
    metrics = json.load(f)
for m in metrics:
    m = m.copy()
    if 'timestamp' in m:
        m['timestamp'] = parse_datetime(m['timestamp'])
    # Remove id if None to let DB autoincrement
    if 'id' in m and (m['id'] is None or m['id'] == ''):
        m.pop('id')
    metric = RouteMetrics(**{k: m[k] for k in RouteMetrics.__table__.columns.keys() if k in m})
    session.merge(metric)
session.commit()
print(f"Imported {len(metrics)} route_metrics.") 