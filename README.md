# ParkIQ — Dynamic Parking Pricing System
## IIT Guwahati Hackathon Project

A full-stack Flask web application for real-time dynamic parking pricing, featuring 3 pricing models, interactive charts, map view, and CSV data ingestion.

---

## Project Structure

```
parking_app/
├── app.py                  # Flask routes & API
├── requirements.txt
├── models/
│   ├── __init__.py
│   └── pricing.py          # All 3 pricing models
└── templates/
    ├── login.html
    └── dashboard.html
```

---

## Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python app.py
```

Open `http://localhost:5000` in your browser.

---

## Login Credentials

| Username | Password   |
|----------|------------|
| admin    | admin123   |
| owner    | owner123   |

---

## CSV Format

Your CSV should contain these columns:

| Column                | Description                        |
|-----------------------|------------------------------------|
| `LastUpdatedDate`     | Date in `DD-MM-YYYY` format        |
| `LastUpdatedTime`     | Time in `HH:MM:SS` format          |
| `Occupancy`           | Number of occupied spots           |
| `Capacity`            | Total capacity of the lot          |
| `QueueLength`         | Cars waiting (optional)            |
| `TrafficConditionNearby` | low / medium / high (optional) |
| `VehicleType`         | car / bike / bus / truck (optional)|
| `IsSpecialDay`        | 0 or 1 (optional)                  |
| `Latitude`            | Lat for geospatial pricing (opt.)  |
| `Longitude`           | Lon for geospatial pricing (opt.)  |

---

## Pricing Models

### 1. Baseline Linear
```
new_price = prev_price + α × (occupancy / capacity)
```
Simple, interpretable model. Price grows proportionally with occupancy.

### 2. Demand-Based
```
demand = 1.2×occ_rate + 0.8×queue − 0.5×traffic + 1.0×special_day + 0.6×vehicle_weight
final_price = base × (1 + λ × normalized_demand)   [clipped to 0.5×base … 2×base]
```
Multi-factor model capturing richer demand signals.

### 3. Competitive
Starts from baseline price, then adjusts based on competitor lots within 500m:
- If occ > 90% AND your price > avg competitor → reduce ₹5 (stay competitive)
- If competitor avg > your price → raise ₹3 (capture market)

---

## Features

- **Real-time updates** — simulates a new data point every 30 seconds
- **CSV upload** — drag & drop your own parking lot CSV
- **3 live charts** — Plotly.js with hover tooltips
- **Map view** — Leaflet + CartoDB dark tiles showing your lot vs competitors
- **Comparison table** — highlights lowest price per timestamp
- **User auth** — Flask-Login with session management

---

## Extending the Project

- Replace the in-memory `USERS` dict with SQLite/PostgreSQL + Flask-SQLAlchemy
- Add real competitor data via a parking API or manual input
- Deploy to Heroku / Render with `gunicorn app:app`
- Add WebSocket (Flask-SocketIO) for true real-time without polling
