import argparse
import json
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from src.database.models import Route, RouteMetrics, Vehicle, Trip
from config.settings import DATABASE_URL

def export_to_csv(route_id=None, start_time=None, end_time=None):
    """Export route metrics to CSV"""
    engine = create_engine(DATABASE_URL)
    session = sessionmaker(engine)()
    
    # Build query
    query = session.query(RouteMetrics)
    if route_id:
        query = query.filter(RouteMetrics.route_id == route_id)
    if start_time:
        query = query.filter(RouteMetrics.timestamp >= start_time)
    if end_time:
        query = query.filter(RouteMetrics.timestamp <= end_time)
    
    # Convert to DataFrame
    df = pd.read_sql(query.statement, query.session.bind)
    
    # Export to CSV
    filename = f"route_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"Data exported to {filename}")

def export_to_json(route_id=None, start_time=None, end_time=None):
    """Export route metrics to JSON"""
    engine = create_engine(DATABASE_URL)
    session = sessionmaker(engine)()
    
    # Build query
    query = session.query(RouteMetrics)
    if route_id:
        query = query.filter(RouteMetrics.route_id == route_id)
    if start_time:
        query = query.filter(RouteMetrics.timestamp >= start_time)
    if end_time:
        query = query.filter(RouteMetrics.timestamp <= end_time)
    
    # Convert to list of dictionaries
    metrics = [
        {
            'route_id': m.route_id,
            'timestamp': m.timestamp.isoformat(),
            'average_delay': m.average_delay,
            'headway_variance': m.headway_variance,
            'bunching_score': m.bunching_score,
            'completion_rate': m.completion_rate
        }
        for m in query.all()
    ]
    
    # Export to JSON
    filename = f"route_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Data exported to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Export MBTA transit data')
    parser.add_argument('--format', choices=['csv', 'json'], required=True,
                      help='Export format (csv or json)')
    parser.add_argument('--route', help='Route ID to export')
    parser.add_argument('--start', help='Start time (YYYY-MM-DD HH:MM:SS)')
    parser.add_argument('--end', help='End time (YYYY-MM-DD HH:MM:SS)')
    
    args = parser.parse_args()
    
    # Parse dates if provided
    start_time = datetime.strptime(args.start, '%Y-%m-%d %H:%M:%S') if args.start else None
    end_time = datetime.strptime(args.end, '%Y-%m-%d %H:%M:%S') if args.end else None
    
    if args.format == 'csv':
        export_to_csv(args.route, start_time, end_time)
    else:
        export_to_json(args.route, start_time, end_time)

if __name__ == "__main__":
    main() 