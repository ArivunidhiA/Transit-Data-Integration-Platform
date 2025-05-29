# MBTA Transit Data Integration Platform

A Python-based platform for collecting, processing, and analyzing real-time MBTA transit data to generate route optimization insights.

## Features

- Real-time data collection from MBTA API
- Local SQLite database storage
- Route efficiency metrics calculation
- Interactive web dashboard
- Data export capabilities
- Automated data collection every 30 seconds

## Prerequisites

- Python 3.9 or higher
- MBTA API key (get one at https://api-v3.mbta.com/)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mbta-transit-platform
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```
MBTA_API_KEY=your_api_key_here
```

## Project Structure

```
mbta-transit-platform/
├── src/
│   ├── collectors/     # Data collection modules
│   ├── processors/     # Data processing logic
│   ├── database/       # Database models and operations
│   ├── analytics/      # Route optimization calculations
│   └── dashboard/      # Web interface
├── data/              # Local data storage
├── config/            # Configuration files
├── tests/             # Unit tests
└── requirements.txt
```

## Usage

1. Initialize the database:
```bash
python src/database/init_db.py
```

2. Start the data collector:
```bash
python src/collectors/main.py
```

3. Launch the dashboard:
```bash
python src/dashboard/main.py
```

4. Access the dashboard at `http://localhost:8000`

## Key Metrics

- Average delay by route and time of day
- Vehicle bunching detection
- Headway analysis
- Route completion times
- Service disruption frequency

## Data Export

Export processed data to CSV/JSON:
```bash
python src/analytics/export_data.py --format csv
```

## Development

Run tests:
```bash
pytest tests/
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 