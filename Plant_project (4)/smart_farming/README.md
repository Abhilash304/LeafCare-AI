# 🌱 AI-Powered Smart Farming Hub

**Offline Disease Detection • Predictive Irrigation • Real-time Monitoring**

A Flask-based web application for smart agriculture that brings together real-time sensor monitoring, machine-learning-powered irrigation prediction, and AI-driven plant disease detection — all accessible from a browser dashboard.

---

## 📋 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Architecture Overview](#-architecture-overview)
- [How Each Module Works](#-how-each-module-works)
  - [1. Flask App (app.py)](#1-flask-app-apppy)
  - [2. Sensor Simulator (sensors_simulator.py)](#2-sensor-simulator-sensors_simulatorpy)
  - [3. Weather Service (weather_service.py)](#3-weather-service-weather_servicepy)
  - [4. Irrigation Predictor (irrigation_predictor.py)](#4-irrigation-predictor-irrigation_predictorpy)
  - [5. Disease Detector (disease_detector.py)](#5-disease-detector-disease_detectorpy)
  - [6. Recommendation Engine (recommendation_engine.py)](#6-recommendation-engine-recommendation_enginepy)
  - [7. Camera Capture (camera_capture.py)](#7-camera-capture-camera_capturepy)
  - [8. Database (database.py)](#8-database-databasepy)
  - [9. Frontend (Dashboard, Disease Detection, History)](#9-frontend-dashboard-disease-detection-history)
- [Data Flow Diagrams](#-data-flow-diagrams)
- [Tech Stack](#-tech-stack)
- [Installation & Setup](#-installation--setup)
- [Running the Application](#-running-the-application)
- [API Endpoints](#-api-endpoints)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Real-time Sensor Dashboard** | Live temperature, humidity, and soil moisture gauges that auto-refresh every 5 seconds |
| **Hybrid Weather Data** | Uses OpenWeatherMap API for real-time weather; falls back to simulation if offline |
| **ML Irrigation Prediction** | RandomForestClassifier predicts irrigation needs based on temperature & humidity |
| **Manual Irrigation Override** | Switch between Auto, ON, and OFF modes from the dashboard |
| **AI Disease Detection** | Upload or capture a leaf photo → HuggingFace MobileNetV2 identifies the disease |
| **Human Detection Guard** | YOLOS-tiny object detector rejects selfies, only accepts plant leaf images |
| **Smart Recommendations** | Returns pesticide/fertilizer advice based on the detected disease |
| **Detection History** | SQLite-backed log of all past disease detections with images |
| **Dark/Light Theme** | Toggle between themes with persistent preference via `localStorage` |
| **Offline Capable** | Falls back to simulated sensors and dummy disease detection when APIs/models are unavailable |

---

## 📁 Project Structure

```
smart_farming/
├── app.py                     # Main Flask application — routes and API endpoints
├── sensors_simulator.py       # Hybrid sensor simulator (Weather API + simulation)
├── weather_service.py         # OpenWeatherMap API client for real-time weather data
├── irrigation_predictor.py    # ML-based irrigation prediction (RandomForestClassifier)
├── disease_detector.py        # Plant disease detection (HuggingFace / TFLite / fallback)
├── recommendation_engine.py   # Pesticide & fertilizer recommendations
├── camera_capture.py          # OpenCV camera capture (server-side fallback)
├── database.py                # SQLite database setup and CRUD operations
├── requirements.txt           # Python dependencies
├── smart_farming.db           # SQLite database file (auto-created)
│
├── models/                    # Saved ML models (auto-generated)
│   └── irrigation_model_v2.pkl
│
├── templates/                 # Jinja2 HTML templates
│   ├── dashboard.html         # Main dashboard with sensor gauges
│   ├── disease.html           # Disease detection page with camera
│   └── history.html           # Detection history table
│
└── static/
    ├── css/
    │   └── style.css          # Global styles, glassmorphism, dark theme
    ├── js/
    │   ├── app.js             # Dashboard JS — ApexCharts gauges + polling
    │   └── disease.js         # Disease page JS — camera, upload, results
    └── uploads/               # Uploaded/captured images (auto-created)
```

---

## 🏗 Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                        BROWSER (Frontend)                      │
│                                                                │
│  dashboard.html ──► app.js (ApexCharts gauges, 5s polling)     │
│  disease.html   ──► disease.js (camera, upload, results)       │
│  history.html   ──► server-rendered Jinja2 templates           │
└──────────────┬────────────────────────┬────────────────────────┘
               │ fetch('/api/sensor-data') │ fetch('/api/capture-and-detect')
               ▼                          ▼
┌────────────────────────────────────────────────────────────────┐
│                     FLASK APP (app.py)                          │
│                                                                │
│  GET  /                    → Dashboard page                    │
│  GET  /disease             → Disease detection page            │
│  GET  /history             → History page                      │
│  GET  /api/sensor-data     → JSON sensor readings              │
│  POST /api/capture-and-detect → JSON disease result (webcam)   │
│  POST /api/upload-and-detect  → JSON disease result (file)     │
│  POST /api/irrigation/toggle  → Toggle irrigation mode         │
│  GET  /api/camera-status      → Camera availability check      │
└──────┬──────┬──────┬──────┬──────┬──────────────────────────────┘
       │      │      │      │      │
       ▼      ▼      ▼      ▼      ▼
  sensors  weather irrig.  disease  recommend.   database
  _simul.  _service predict. _detect. _engine     .py
   .py      .py     .py      .py      .py         (SQLite)
```

---

## 🔧 How Each Module Works

### 1. Flask App (`app.py`)

The central hub that wires everything together.

**Routes served:**
- `/` — Renders `dashboard.html` (sensor overview)
- `/disease` — Renders `disease.html` (camera + detection)
- `/history` — Renders `history.html` (past detections from DB)

**API endpoints:**
- `GET /api/sensor-data` — Calls `sensor_simulator.read_all()`, computes status colors (good/warning/critical), returns JSON with temperature, humidity, soil moisture, irrigation prediction, and timestamps.
- `POST /api/capture-and-detect` — Accepts a base64-encoded webcam image OR falls back to OpenCV capture; runs disease detection → recommendation → stores in DB → returns results.
- `POST /api/upload-and-detect` — Accepts a file upload; same pipeline as above.
- `POST /api/irrigation/toggle` — Switches between Auto and Manual irrigation modes.

**Error handling:** Every API route is wrapped in `try/except`. The sensor API returns safe defaults (200 status) even on failure so the frontend never breaks.

**Startup:** Initializes the SQLite database, creates the uploads directory, and starts the Flask dev server on `0.0.0.0:5000`.

---

### 2. Sensor Simulator (`sensors_simulator.py`)

A **hybrid** sensor system that combines real API data with simulation.

**How it works:**

1. **Temperature & Humidity** — Fetched from OpenWeatherMap via `weather_service.py`. If the API call fails (no internet, rate limit), it falls back to a random-walk simulation that drifts values within realistic ranges (25–40°C, 40–95% humidity).

2. **Soil Moisture** — Always simulated. It decreases slowly over time (evaporation) and increases when irrigation is ON, bounded between 20–95%.

3. **Irrigation Prediction** — After reading sensors, it calls `irrigation_predictor.predict()` to get an ML-based recommendation on whether irrigation is needed.

4. **Database Logging** — Every sensor reading and irrigation decision is stored in SQLite for historical tracking.

5. **Manual Override** — The `set_manual_override(mode, status)` method allows the dashboard to force irrigation ON/OFF regardless of the ML prediction.

**Singleton pattern:** A single `sensor_simulator` instance is created at module level and imported by `app.py`.

---

### 3. Weather Service (`weather_service.py`)

Fetches **real-time weather data** from the OpenWeatherMap API.

**How it works:**
- Uses precise latitude/longitude coordinates for **Mangalore, India** (12.9141°N, 74.8560°E) instead of city-name lookup for higher accuracy.
- API call: `http://api.openweathermap.org/data/2.5/weather?lat=...&lon=...&units=metric`
- Returns temperature (°C) and humidity (%) as floats.
- Includes a 10-second timeout to avoid blocking the server.
- Returns `None` on any failure (network error, invalid key, timeout), which triggers the fallback simulation in `sensors_simulator.py`.

---

### 4. Irrigation Predictor (`irrigation_predictor.py`)

An **offline ML model** using scikit-learn's `RandomForestClassifier`.

**How it works:**

1. **Training Data** — Generates 1000 synthetic samples with temperature (15–45°C), humidity (20–95%), and hour (0–23). Labels follow the rule: irrigation is needed if `temperature > 32` OR (`temperature > 28` AND `humidity < 50`).

2. **Model Training** — Trains a RandomForest with 100 estimators on first use if no saved model exists.

3. **Model Persistence** — Saves the trained model to `models/irrigation_model_v2.pkl` using joblib. On subsequent starts, it loads the saved model instead of retraining.

4. **Prediction** — Takes current temperature and humidity, returns:
   ```json
   {
     "irrigation_needed": true/false,
     "confidence": 0.0 - 1.0
   }
   ```

5. **Lazy Loading** — The model is loaded/trained on the first prediction call, not at import time, to keep server startup fast.

---

### 5. Disease Detector (`disease_detector.py`)

A **multi-tier detection system** with intelligent fallbacks.

**Detection Pipeline (in priority order):**

```
Image → Human Check (YOLOS-tiny) → HuggingFace Model → TFLite Model → Color Analysis Fallback
```

**Tier 1: Human Detection Guard**
- Uses `hustvl/yolos-tiny` object detection model
- If a "person" is detected with >75% confidence AND occupies >50% of the frame, the image is rejected with "Please upload a photo focusing on the plant leaf"
- Allows hands/arms holding leaves (they won't occupy >50% of the frame)

**Tier 2: HuggingFace Plant Disease Model**
- Model: `linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification`
- Uses MobileNetV2 architecture for efficient inference
- Returns labels like `Tomato___Late_blight` which are parsed into crop name + disease name
- Global caching: model/processor/pipeline are loaded once and reused for all subsequent requests

**Tier 3: TFLite Model (Optional)**
- Loads a local `.tflite` model from `model/plant_disease_model.tflite` if present
- Preprocesses images to 224×224, normalizes to [0,1]
- Useful for edge deployments (Raspberry Pi)

**Tier 4: Color Analysis Fallback (No ML needed)**
- Analyzes leaf color using image heuristics:
  - **Green dominance ratio** — Healthy leaves have dominant green channel
  - **Red-to-green ratio** — Yellowing/browning indicates disease
  - **Color variance** — Spots/lesions cause high local color variance
  - **Block variance** — Image is split into a 4×4 grid to detect uneven coloring
- Produces a disease score (0–1); scores ≥0.35 are classified as diseased
- Maps to specific diseases (Leaf Blight, Bacterial Spot, etc.) based on severity

**Confidence Threshold:** Results with confidence <60% return a "Low Confidence - Retake Image" status, shown as a warning banner in the UI.

---

### 6. Recommendation Engine (`recommendation_engine.py`)

Provides **actionable advice** based on the disease detection result.

**For Healthy Plants:**
- Recommends a random fertilizer from a curated list (NPK 19:19:19, Urea, DAP, Potash, Organic Compost)
- Includes quantity, timing, and 5 preventive tips

**For Diseased Plants:**
- Looks up the disease in a knowledge base covering: Leaf Blight, Bacterial Spot, Early Blight, Late Blight, Powdery Mildew, and Leaf Spot
- Returns: cause, recommended pesticide, usage instructions, and preventive measures
- Falls back to "Leaf Spot" recommendations for unknown diseases

---

### 7. Camera Capture (`camera_capture.py`)

Server-side **OpenCV camera capture** as a fallback when the browser webcam isn't available.

**How it works:**
- Opens `VideoCapture(0)` (laptop's built-in camera)
- Reads 3 frames to allow auto-focus to settle
- Saves the captured frame as a JPEG (`capture_YYYYMMDD_HHMMSS.jpg`)
- The browser's `getUserMedia` webcam is the primary path; this is only used if the browser can't access the camera

---

### 8. Database (`database.py`)

SQLite database with **3 tables** — no external database server needed.

**Tables:**

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `sensor_readings` | Historical sensor data | temperature, humidity, soil_moisture, timestamp |
| `irrigation_logs` | Irrigation ON/OFF history | status, soil_moisture, reason, prediction_confidence |
| `disease_detections` | Past disease results | image_path, disease_name, confidence, health_status, recommendation |

**Features:**
- Context manager (`get_db()`) ensures proper connection cleanup
- Auto-migration for schema changes (e.g., adding `prediction_confidence` column)
- Row factory returns dictionaries for easy JSON serialization

---

### 9. Frontend (Dashboard, Disease Detection, History)

#### Dashboard (`dashboard.html` + `app.js`)
- **3 ApexCharts radial gauges** for Temperature (°C), Humidity (%), and Soil Moisture (%)
- **Sensor cards** with color-coded status badges (Good/Warning/Critical)
- **Irrigation status** with Auto/ON/OFF toggle buttons
- **AI Prediction card** showing the ML model's irrigation recommendation with confidence bar
- **Location & timestamp** showing data source and last update time
- **Auto-refresh** every 5 seconds via `fetch('/api/sensor-data')`
- **Header widgets** showing real-time weather and system status

#### Disease Detection (`disease.html` + `disease.js`)
- **Live camera preview** using `getUserMedia`
- **Capture & Detect button** — captures frame from webcam → base64 → POST to `/api/capture-and-detect`
- **Upload Image button** — file upload → FormData → POST to `/api/upload-and-detect`
- **Optional plant name input** for more precise results
- **Result panel** showing crop name, disease, confidence, health badge, and smart recommendation
- **Low-confidence warning banner** when model isn't sure

#### History (`history.html`)
- Server-rendered table of past detections
- Shows image thumbnail, disease name, confidence, health status, and timestamp
- Parsed recommendations displayed inline

---

## 📊 Data Flow Diagrams

### Sensor Data Flow (Every 5 Seconds)

```
Browser (app.js)
    │
    ├── fetch('/api/sensor-data')  ─────────────────────┐
    │                                                    ▼
    │                                            app.py (Flask)
    │                                                    │
    │                                    sensor_simulator.read_all()
    │                                         │         │         │
    │                                         ▼         ▼         ▼
    │                                    WeatherAPI  Soil Sim  ML Predict
    │                                    (real data) (random)  (sklearn)
    │                                         │         │         │
    │                                         ▼         ▼         ▼
    │                                    ┌─── database.py (SQLite) ──┐
    │                                    │  sensor_readings table     │
    │                                    │  irrigation_logs table     │
    │                                    └───────────────────────────┘
    │                                                    │
    │◄── JSON { temperature, humidity,  ◄────────────────┘
    │          soil_moisture, irrigation_status, ... }
    │
    ├── Update ApexCharts gauges
    ├── Update status badges
    └── Update irrigation display
```

### Disease Detection Flow

```
Browser (disease.js)
    │
    ├── Webcam frame (base64) ──► POST /api/capture-and-detect
    │   or File upload ─────────► POST /api/upload-and-detect
    │                                        │
    │                                        ▼
    │                              disease_detector.py
    │                                        │
    │                          ┌─────────────┼──────────────┐
    │                          ▼             ▼              ▼
    │                    YOLOS-tiny    HuggingFace     Color Analysis
    │                    (human?)     MobileNetV2      (fallback)
    │                          │             │              │
    │                          ▼             ▼              ▼
    │                    Reject if      Disease +       Disease +
    │                    human         Confidence       Confidence
    │                                        │
    │                                        ▼
    │                             recommendation_engine.py
    │                                        │
    │                                        ▼
    │                               database.py (store)
    │                                        │
    │◄── JSON { crop, disease,  ◄────────────┘
    │          confidence, health_status,
    │          recommendation }
    │
    ├── Show result panel
    ├── Show health badge (Healthy/Diseased)
    └── Show recommendation (pesticide/fertilizer)
```

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10+, Flask 3.x |
| **Database** | SQLite (zero configuration) |
| **ML - Irrigation** | scikit-learn (RandomForestClassifier), joblib |
| **ML - Disease Detection** | HuggingFace Transformers, PyTorch, MobileNetV2 |
| **ML - Human Detection** | YOLOS-tiny (object detection) |
| **Weather API** | OpenWeatherMap (free tier) |
| **Camera** | OpenCV (server-side fallback), getUserMedia (browser) |
| **Frontend** | Bootstrap 5.3, ApexCharts (gauges), Chart.js, Bootstrap Icons |
| **Image Processing** | Pillow, NumPy |

---

## 📦 Installation & Setup

### Prerequisites
- **Python 3.10 or higher** (tested on 3.10–3.13)
- **pip** (Python package manager)
- **Webcam** (optional — for live disease detection)

### Steps

1. **Navigate to the project directory:**
   ```bash
   cd smart_farming
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv

   # Activate on Windows:
   venv\Scripts\activate

   # Activate on macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   > **Note:** If you only need sensor monitoring (no AI disease detection), use:
   > ```bash
   > pip install -r requirements-minimal.txt
   > ```
   > The app will fall back to color-analysis-based disease detection.

---

## ▶ Running the Application

```bash
python app.py
```

The server starts on **http://127.0.0.1:5000/**

```
==================================================
  AI-Powered Smart Farming Hub
  Dashboard: http://127.0.0.1:5000/
  Disease Detection: http://127.0.0.1:5000/disease
==================================================
```

| Page | URL |
|------|-----|
| Dashboard | http://127.0.0.1:5000/ |
| Disease Detection | http://127.0.0.1:5000/disease |
| History | http://127.0.0.1:5000/history |

---

## 📡 API Endpoints

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `GET` | `/api/sensor-data` | Current sensor readings | `{ temperature, humidity, soil_moisture, irrigation_status, ... }` |
| `POST` | `/api/capture-and-detect` | Disease detection from webcam | `{ success, crop, disease, confidence, health_status, recommendation }` |
| `POST` | `/api/upload-and-detect` | Disease detection from file upload | Same as above |
| `POST` | `/api/irrigation/toggle` | Toggle irrigation mode | `{ success, message }` |
| `GET` | `/api/camera-status` | Check if server camera is available | `{ available: true/false }` |

### Example: Sensor Data Response
```json
{
  "temperature": 29.5,
  "humidity": 70.0,
  "soil_moisture": 52.3,
  "temp_status": "good",
  "humidity_status": "good",
  "irrigation_status": "OFF",
  "irrigation_prediction": false,
  "irrigation_confidence": 0.92,
  "manual_mode": false,
  "data_source": "Weather API (Mangalore)",
  "timestamp": "2026-03-14 11:30:00"
}
```

### Example: Disease Detection Response
```json
{
  "success": true,
  "image_path": "/static/uploads/capture_20260314_113000.jpg",
  "crop": "Tomato",
  "disease": "Late Blight",
  "disease_name": "Late Blight",
  "confidence": 87.5,
  "health_status": "Diseased",
  "status": "ok",
  "recommendation": {
    "type": "diseased",
    "cause": "Oomycete (Phytophthora infestans)...",
    "pesticide": "Metalaxyl + Mancozeb...",
    "usage": "Apply as per label...",
    "preventive_tips": ["Avoid wetting foliage..."]
  }
}
```

---

## ⚙ Configuration

| Setting | Location | Default |
|---------|----------|---------|
| OpenWeatherMap API key | `sensors_simulator.py` line 17 | Pre-configured |
| City/Coordinates | `weather_service.py` lines 13–14 | Mangalore (12.9141°N, 74.8560°E) |
| HuggingFace model | `disease_detector.py` line 20 | `linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification` |
| HuggingFace token | `disease_detector.py` line 21 | Pre-configured |
| Flask port | `app.py` line 323 | 5000 |
| Max upload size | `app.py` line 21 | 16 MB |
| Sensor refresh interval | `static/js/app.js` line 8 | 5000 ms (5 seconds) |
| Database path | `database.py` line 12 | `smart_farming.db` (project root) |

---

## 🔍 Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Dashboard gauges show `--` | `/api/sensor-data` returning error | Check Flask terminal for errors; ensure `database.py` can write to disk |
| "Network error" on disease detect | Flask reloader restarting during PyTorch import | Change `app.run(debug=True)` to `app.run(debug=True, use_reloader=False)` |
| "Upload error" on file upload | Same as above — server restarts mid-request | Same fix: `use_reloader=False` |
| Camera not showing | Browser blocked camera access | Allow camera permission in browser; or check if another app is using the webcam |
| HuggingFace model slow on first use | Model downloads ~100MB on first inference | Wait for download to complete; subsequent runs use the cached model |
| `ModuleNotFoundError: torch` | PyTorch not installed | Run `pip install torch transformers`; the app will fall back to color analysis if not installed |
| Sensor data shows "Simulated (Fallback)" | Weather API call failed | Check internet connection; the OpenWeatherMap free tier has a rate limit |

---

## 📝 License

This project was developed as a Final Year Academic Project.

---

*Built with ❤️ using Flask, HuggingFace Transformers, scikit-learn, and ApexCharts*
