# 🚇 MBTA Transit Telemetry Platform

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Node](https://img.shields.io/badge/node-18+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.124-blue)
![React](https://img.shields.io/badge/React-18-blue)

> Real-time telemetry collection and observability platform for MBTA transit vehicles. Collects, processes, and visualizes live transit data with 10-second update intervals.

![Dashboard Screenshot 1](Screenshot%202025-12-10%20at%204.09.46%20PM.png)
![Dashboard Screenshot 2](Screenshot%202025-12-10%20at%204.10.06%20PM.png)

## 📑 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Deployment](#-deployment)
- [Development](#-development)

## 🎯 Overview

The MBTA Transit Telemetry Platform is a full-stack application that provides real-time monitoring and analytics for Boston's public transit system. It collects vehicle positions, calculates route delays, detects anomalies, and presents insights through an interactive dashboard.

**Key Highlights:**
- ⚡ **Real-time data collection** every 10 seconds from MBTA API
- 📊 **Interactive dashboards** with live vehicle maps and analytics
- 🔍 **Anomaly detection** for route delays and service disruptions
- 📈 **Time-series analysis** for historical pattern recognition
- 🎨 **Modern UI** with dark/light theme support

## ✨ Features

### 📡 Data Collection
- Automated telemetry collection from MBTA API
- Bulk database operations for optimal performance
- Retry logic with exponential backoff
- Real-time status tracking for 100+ vehicles

### 📊 Analytics & Visualization
- **Overview Dashboard**: System health, uptime, vehicle count
- **Live Vehicle Map**: Interactive map with GPS positions using Leaflet
- **Route Analytics**: Delay patterns and headway analysis
- **Time-Series Explorer**: Historical data visualization with Recharts

### 🛡️ Reliability
- Error boundaries and graceful error handling
- Health check endpoints for monitoring
- Rate limit handling and automatic retries
- Comprehensive logging

### 🎨 User Experience
- Skeleton loaders for better perceived performance
- Real-time indicators ("Live" badges)
- Dark/light theme toggle
- Keyboard shortcuts for navigation
- Responsive design

## 🏗️ Architecture

```
┌─────────────────┐
│   MBTA API      │
│  (External)     │
└────────┬────────┘
         │ HTTP/HTTPS
         ▼
┌─────────────────────────────────┐
│   Data Collector Service        │
│   (Python + APScheduler)        │
│   • Fetches every 10s           │
│   • Bulk upserts                │
│   • Delay calculation           │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   SQLite Database               │
│   • vehicles                    │
│   • telemetry_events            │
│   • route_delays                │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│   FastAPI Backend               │
│   • REST API endpoints          │
│   • Health monitoring           │
│   • CORS enabled                │
└────────┬────────────────────────┘
         │ HTTP/REST
         ▼
┌─────────────────────────────────┐
│   React Frontend                │
│   • TanStack Query              │
│   • Real-time updates           │
│   • Interactive dashboards      │
└─────────────────────────────────┘
```

### Component Overview

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Collector** | Python + APScheduler | Scheduled data collection from MBTA API |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Time-series data storage |
| **Backend API** | FastAPI + Uvicorn | RESTful API with auto-docs |
| **Frontend** | React + Vite + TypeScript | Modern SPA with real-time updates |
| **Maps** | Leaflet + React-Leaflet | Interactive vehicle positioning |
| **Charts** | Recharts | Data visualization |

## 🛠️ Tech Stack

### Backend
- **FastAPI** 0.124 - Modern Python web framework
- **SQLAlchemy** 2.0 - Database ORM
- **APScheduler** 3.11 - Background task scheduling
- **httpx** 0.28 - Async HTTP client
- **Pydantic** 2.12 - Data validation

### Frontend
- **React** 18 - UI framework
- **TypeScript** 5.2 - Type safety
- **Vite** 5.0 - Build tool
- **TanStack Query** 5.12 - Data fetching & caching
- **Tailwind CSS** 3.3 - Utility-first styling
- **Leaflet** 1.9 - Maps
- **Recharts** 2.10 - Charts

### Infrastructure
- **Render** - Backend hosting
- **Netlify** - Frontend hosting
- **GitHub Actions** - CI/CD

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MBTA API key ([Get one here](https://api-v3.mbta.com/register))

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/ArivunidhiA/Transit-Data-Integration-Platform.git
cd Transit-Data-Integration-Platform
```

**2. Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
```

**3. Frontend Setup**
```bash
cd ../frontend
npm install
```

**4. Configure Environment**
```bash
# Backend (.env in backend/)
MBTA_API_KEY=your_api_key_here

# Frontend (.env in frontend/)
VITE_API_URL=http://localhost:8000
```

**5. Start Services**
```bash
# Terminal 1: Backend
cd backend && uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

**6. Access the Application**
- Frontend: http://localhost:3000 (or port shown)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## ⚙️ Configuration

### Backend Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `MBTA_API_KEY` | ✅ | - | MBTA API key for data access |
| `DATABASE_URL` | ❌ | `sqlite:///./data/mbta_telemetry.db` | Database connection string |
| `CORS_ORIGINS` | ❌ | `*` | Allowed CORS origins (comma-separated) |
| `LOG_LEVEL` | ❌ | `INFO` | Logging level |

**Example `.env` files:**
```env
# backend/.env
MBTA_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./data/mbta_telemetry.db
CORS_ORIGINS=http://localhost:3000

# frontend/.env
VITE_API_URL=http://localhost:8000
```

## 🚢 Deployment

### Render + Netlify (Recommended)

**Backend (Render):** Connect GitHub repo → Create Web Service → Root `backend` → Build `pip install -r requirements.txt` → Start `uvicorn main:app --host 0.0.0.0 --port $PORT` → Set env vars

**Frontend (Netlify):** Connect GitHub repo → Base `frontend` → Build `npm run build` → Publish `dist` → Set `VITE_API_URL`

**Docker Compose:**
```bash
docker-compose up -d
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 💻 Development

### Project Structure

```
Transit-Data-Integration-Platform/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── collector.py         # Data collection service
│   ├── database.py          # SQLAlchemy models
│   ├── services/            # Business logic
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/           # Route pages
│   │   ├── components/      # Reusable components
│   │   ├── hooks/           # Custom React hooks
│   │   ├── lib/             # API client & schemas
│   │   └── utils/           # Helper functions
│   └── package.json
└── README.md
```

### Local Development

**Backend**
```bash
cd backend && uvicorn main:app --reload --port 8000
```

**Frontend**
```bash
cd frontend && npm run dev
```

**Testing:** `cd backend && pytest tests/` | `cd frontend && npm run lint`

### Key API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/vehicles` | GET | Active vehicles |
| `/analytics/system` | GET | System metrics |
| `/routes/{id}/delays` | GET | Route delays |
| `/alerts` | GET | System alerts |

## 📄 License

MIT License

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**Built with ❤️ for the MBTA transit community**
