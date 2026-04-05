# 🅿️ ParkIQ — Dynamic Parking Pricing System

## 🏆 IIT Guwahati Hackathon Project

🚗 A full-stack Flask web application for real-time dynamic parking pricing, featuring 3 intelligent pricing models, interactive charts, map view, and CSV data ingestion.

---

## 📌 Overview

💡 ParkIQ solves the problem of static, inefficient parking pricing by dynamically adjusting prices based on real-time occupancy, demand signals, and competitor data. Built for the IIT Guwahati Hackathon, it brings smart pricing to parking lots.

🔗 **GitHub Repository:** [tanishcode-12/ParkIQ](https://github.com/tanishcode-12/ParkIQ)

---

## ✨ Features

- ⏱️ **Real-time updates** — simulates a new data point every 30 seconds
- 📂 **CSV upload** — drag & drop your own parking lot CSV
- 📊 **3 live charts** — Plotly.js with hover tooltips
- 🗺️ **Map view** — Leaflet + CartoDB dark tiles showing your lot vs competitors
- 📋 **Comparison table** — highlights lowest price per timestamp
- 🔐 **User auth** — Flask-Login with session management
- 🧠 **3 pricing models** — Baseline, Demand-Based, and Competitive

---

## 🗂️ Project Structure

```
🅿️ parking_app/
├── 🐍 app.py                  # Flask routes & API
├── 📄 requirements.txt
├── 📁 models/
│   ├── 🐍 __init__.py
│   └── 🐍 pricing.py          # All 3 pricing models
└── 📁 templates/
    ├── 🌐 login.html
    └── 🌐 dashboard.html
```

---

## ⚙️ Setup

### 🧰 Prerequisites

- 🐍 Python 3.8+
- 📦 pip

### 🪜 Steps

1. **📥 Clone the repository**

```bash
git clone https://github.com/tanishcode-12/ParkIQ.git
cd ParkIQ/parking_app
```

2. **🧪 Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

3. **📦 Install dependencies**

```bash
pip install -r requirements.txt
```

4. **▶️ Run the app**

```bash
python app.py
```

5. **🌐 Open in your browser**

```
http://localhost:5000
```

---

## 🔐 Login Credentials

| 👤 Username | 🔑 Password |
|-------------|-------------|
| `admin`     | `admin123`  |
| `owner`     | `owner123`  |

---

## 📄 CSV Format

📂 Your CSV file should contain the following columns:

| 📋 Column | 📝 Description |
|---|---|
| `LastUpdatedDate` | 📅 Date in `DD-MM-YYYY` format |
| `LastUpdatedTime` | 🕐 Time in `HH:MM:SS` format |
| `Occupancy` | 🚗 Number of occupied spots |
| `Capacity` | 🏗️ Total capacity of the lot |
| `QueueLength` | 🚦 Cars waiting *(optional)* |
| `TrafficConditionNearby` | 🛣️ `low` / `medium` / `high` *(optional)* |
| `VehicleType` | 🚌 `car` / `bike` / `bus` / `truck` *(optional)* |
| `IsSpecialDay` | 🎉 `0` or `1` *(optional)* |
| `Latitude` | 🌍 Lat for geospatial pricing *(optional)* |
| `Longitude` | 🌍 Lon for geospatial pricing *(optional)* |

---

## 🧠 Pricing Models

### 1️⃣ Baseline Linear

```
new_price = prev_price + α × (occupancy / capacity)
```

📈 Simple, interpretable model. Price grows proportionally with occupancy.

---

### 2️⃣ Demand-Based

```
demand = 1.2×occ_rate + 0.8×queue − 0.5×traffic + 1.0×special_day + 0.6×vehicle_weight
final_price = base × (1 + λ × normalized_demand)   [clipped to 0.5×base … 2×base]
```

📊 Multi-factor model capturing richer demand signals including traffic, vehicle type, and special events.

---

### 3️⃣ Competitive

🏆 Starts from baseline price, then adjusts based on competitor lots within **500m**:

- 📉 If occupancy > 90% **AND** your price > avg competitor → reduce ₹5 *(stay competitive)*
- 📈 If competitor avg > your price → raise ₹3 *(capture market)*

---

## 🚀 Extending the Project

🔧 Want to take ParkIQ further? Here are some ideas:

- 🗄️ Replace the in-memory `USERS` dict with **SQLite/PostgreSQL** + Flask-SQLAlchemy
- 📡 Add real competitor data via a **parking API** or manual input
- ☁️ Deploy to **Heroku / Render** with `gunicorn app:app`
- 🔌 Add **WebSocket** (Flask-SocketIO) for true real-time without polling

---

## 🤝 Contributing

🙌 Contributions are welcome! Here's how you can help:

1. 🍴 Fork the repository
2. 🌿 Create a new branch (`git checkout -b feature/your-feature`)
3. 💾 Make your changes and commit (`git commit -m 'Add your feature'`)
4. 📤 Push to the branch (`git push origin feature/your-feature`)
5. 🔁 Open a Pull Request

✅ Please make sure your code is clean and well-commented.

---

## 👤 Author

**Tanish** — [@tanishcode-12](https://github.com/tanishcode-12)

---

> ⭐ If you found ParkIQ helpful, consider giving it a star on GitHub!
