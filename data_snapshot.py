import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Route, Vehicle, Trip, Stop, Alert, RouteMetrics
from config.settings import DATABASE_URL

engine = create_engine(DATABASE_URL)
session = sessionmaker(engine)()

def export_table(model, filename):
    data = session.query(model).all()
    result = [
        {col.name: getattr(row, col.name) for col in model.__table__.columns}
        for row in data
    ]
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"Exported {len(result)} records to {filename}")

if __name__ == "__main__":
    export_table(Route, 'routes.json')
    export_table(Vehicle, 'vehicles.json')
    export_table(Trip, 'trips.json')
    export_table(Stop, 'stops.json')
    export_table(Alert, 'alerts.json')
    export_table(RouteMetrics, 'route_metrics.json') 