# 🌿 LeafCare AI — AI-Powered Smart Farming Hub

> **Offline Plant Disease Detection · ML-Based Predictive Irrigation · Real-Time Sensor Monitoring**

A comprehensive, AI-driven smart agriculture platform that combines deep-learning plant disease identification, machine-learning-based irrigation prediction, real-time IoT sensor simulation, and intelligent crop-care recommendations — all running locally on your machine with zero cloud dependency after initial model download.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [Tech Stack](#️-tech-stack)
- [System Architecture](#-system-architecture)
- [Project Structure](#-project-structure)
- [Module Descriptions](#-module-descriptions)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Running the Application](#-running-the-application)
- [API Reference](#-api-reference)
- [Screenshots](#-screenshots)
- [How It Works](#-how-it-works)
- [Configuration](#️-configuration)
- [Testing](#-testing)
- [Troubleshooting](#-troubleshooting)
- [Future Enhancements](#-future-enhancements)
- [License](#-license)
- [Contributors](#-contributors)

---

## 🌟 Key Features

### 🔬 AI-Powered Plant Disease Detection
- Uses **Hugging Face Transformers** with a fine-tuned **MobileNetV2** model (`linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification`)
- Identifies **38+ plant diseases** across multiple crop species (Tomato, Potato, Apple, Corn, Grape, etc.)
- **YOLOS-tiny object detection** pre-filter to reject non-plant images (e.g., humans, objects)
- Fallback: **TensorFlow Lite** local model → **Color-heuristic image analysis** → ensures the system always works, even completely offline
- Supports both **webcam capture** and **file upload** workflows

### 📊 Real-Time Sensor Dashboard
- Live monitoring of **Temperature** and **Humidity** with simulated sensor drift for realism
- Color-coded status indicators (Good / Warning / Critical) based on agricultural thresholds
- Auto-refreshing dashboard via **AJAX polling** every 5 seconds

### 💧 ML-Based Predictive Irrigation
- **Random Forest Classifier** trained on 1,000 synthetic samples
- Predicts irrigation need based on temperature, humidity, and time-of-day
- Supports **Auto** and **Manual Override** modes
- Displays prediction confidence in real-time

### 📋 Detection History & Analytics
- Full chronological log of all disease detections stored in **SQLite**
- View captured images, confidence scores, health status, and treatment recommendations
- Up to 50 most recent records displayed with parsed recommendation data

### 💊 Smart Recommendation Engine
- **Diseased plants**: Prescribes specific pesticides/fungicides with dosage, usage frequency, and preventive measures
- **Healthy plants**: Recommends fertilizers (NPK, Urea, DAP, Potash, Organic Compost) with application timing and tips
- Covers 6+ common diseases: Leaf Blight, Bacterial Spot, Early Blight, Late Blight, Powdery Mildew, Leaf Spot

### 🔌 Offline-First Design
- All AI models cached locally after first download
- No internet required for day-to-day operation
- SQLite database — no external database server needed

---

## 🛠️ Tech Stack

| Layer              | Technology                                                                              |
| ------------------ | --------------------------------------------------------------------------------------- |
| **Backend**        | Python 3.8+, Flask 3.x                                                                 |
| **AI / ML**        | Hugging Face Transformers, PyTorch, MobileNetV2, YOLOS-tiny, TensorFlow Lite (fallback)|
| **Irrigation ML**  | scikit-learn (Random Forest Classifier), joblib                                         |
| **Database**       | SQLite 3 (sensor readings, irrigation logs, disease detections)                         |
| **Camera**         | OpenCV (`cv2`) — laptop built-in webcam + browser MediaStream API                       |
| **Frontend**       | HTML5, CSS3, Bootstrap 5, JavaScript (AJAX / Fetch API)                                 |
| **Image Processing**| Pillow (PIL), NumPy                                                                    |

---

## 🏗 System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        BROWSER (Frontend)                        │
│  ┌──────────────┐  ┌──────────────────┐  ┌───────────────────┐  │
│  │  Dashboard    │  │ Disease Detection│  │   History Page    │  │
│  │  (AJAX poll)  │  │ (Webcam/Upload)  │  │  (Detection Logs) │  │
│  └──────┬───────┘  └────────┬─────────┘  └────────┬──────────┘  │
└─────────┼──────────────────┼──────────────────────┼─────────────┘
          │ GET /api/        │ POST /api/           │ GET /history
          │ sensor-data      │ capture-and-detect   │
          ▼                  ▼                      ▼
┌──────────────────────────────────────────────────────────────────┐
│                      FLASK APPLICATION (app.py)                  │
│  ┌────────────────┐  ┌─────────────────┐  ┌──────────────────┐  │
│  │ Sensor         │  │ Disease         │  │ Recommendation   │  │
│  │ Simulator      │  │ Detector        │  │ Engine           │  │
│  │ + Irrigation   │  │ (HF/TFLite/     │  │ (Pesticides/     │  │
│  │   Predictor    │  │  Heuristic)     │  │  Fertilizers)    │  │
│  └───────┬────────┘  └────────┬────────┘  └────────┬─────────┘  │
└──────────┼─────────────────────┼───────────────────┼────────────┘
           │                     │                   │
           ▼                     ▼                   ▼
┌──────────────────────────────────────────────────────────────────┐
│                     SQLite DATABASE                               │
│   sensor_readings  │  irrigation_logs  │  disease_detections     │
└──────────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
smart_farming/
│
├── app.py                      # Main Flask application & API routes
├── database.py                 # SQLite setup, CRUD operations
├── disease_detector.py         # Multi-tier disease detection engine
├── sensors_simulator.py        # Realistic sensor data simulator
├── irrigation_predictor.py     # ML-based irrigation prediction (Random Forest)
├── recommendation_engine.py    # Smart cure & care recommendation logic
├── camera_capture.py           # OpenCV-based webcam capture module
│
├── requirements.txt            # Full project dependencies
├── requirements-minimal.txt    # Minimal dependencies (no TensorFlow)
├── smart_farming.db            # SQLite database (auto-created)
│
├── model/                      # TFLite model storage (optional)
│   └── plant_disease_model.tflite
│
├── models/                     # ML model storage
│   └── irrigation_model_v2.pkl # Trained Random Forest model (auto-generated)
│
├── templates/                  # Jinja2 HTML templates
│   ├── dashboard.html          # Real-time sensor monitoring UI
│   ├── disease.html            # Camera capture & analysis interface
│   └── history.html            # Detection history dashboard
│
├── static/
│   ├── css/
│   │   └── style.css           # Core application styling
│   ├── js/
│   │   ├── dashboard.js        # Dashboard AJAX & chart logic
│   │   └── disease.js          # Disease detection frontend logic
│   └── uploads/                # Saved leaf captures & uploads
│
├── test_api.py                 # API endpoint tests
├── test_api_upload.py          # File upload API tests
├── test_detection.py           # Disease detection unit tests
├── test_hf.py                  # Hugging Face integration tests
├── test_hf_non_leaf.py         # Non-leaf image rejection tests
└── test_human.py               # Human detection rejection tests
```

---

## 📦 Module Descriptions

### `app.py` — Flask Application Server
The central entry point. Defines all web routes and API endpoints. Initializes the SQLite database on startup, serves the dashboard/disease/history pages, and orchestrates the detection pipeline (capture → detect → recommend → store).

### `disease_detector.py` — Multi-Tier Detection Engine
Implements a **three-level fallback** strategy:
1. **Hugging Face Transformers** (Primary) — MobileNetV2 image classification pipeline with YOLOS-tiny human-detection pre-filter
2. **TensorFlow Lite** (Secondary) — Local `.tflite` model inference
3. **Color Heuristic Analysis** (Fallback) — Analyzes green dominance, R/G ratio, color variance, and block-level spot detection to classify leaf health

Parses HF labels (e.g., `Tomato___Late_blight`) into structured crop + disease output.

### `sensors_simulator.py` — Sensor Data Simulator
Generates realistic, smoothly drifting temperature (25–40°C) and humidity (40–90%) values without real hardware. Integrates with the irrigation predictor for automated or manual irrigation control.

### `irrigation_predictor.py` — ML Irrigation Predictor
Trains a **Random Forest Classifier** on 1,000 synthetic data points with rules:
- Irrigation ON if Temperature > 32°C **OR** (Temperature > 28°C **AND** Humidity < 50%)
- Persists the trained model as `irrigation_model_v2.pkl` using joblib
- Auto-trains on first run if no saved model exists

### `recommendation_engine.py` — Treatment Recommendations
Returns tailored advice based on detection results:
- **Diseased**: Cause, pesticide name, dosage/usage, preventive measures
- **Healthy**: Fertilizer type, quantity per acre, application timing, care tips

### `camera_capture.py` — Webcam Capture
Uses OpenCV `VideoCapture(0)` to grab frames from the laptop's built-in camera. Includes warm-up frames for auto-focus and graceful error handling.

### `database.py` — SQLite Data Layer
Manages three tables:
- `sensor_readings` — Temperature, humidity, soil moisture readings
- `irrigation_logs` — Irrigation ON/OFF events with ML confidence scores
- `disease_detections` — Captured images, disease names, confidence, recommendations

---

## ✅ Prerequisites

- **Python 3.8** or higher (3.10–3.12 recommended for full TensorFlow support)
- **pip** package manager
- **Laptop webcam** (optional — file upload works without a camera)
- **~2 GB disk space** for PyTorch + Hugging Face model downloads on first run
- **Internet connection** for initial model download only (offline afterward)

---

## 🚀 Installation & Setup

### 1. Clone or Extract the Project

```bash
cd smart_farming
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

**Full installation** (with TensorFlow + PyTorch + Transformers):
```bash
pip install -r requirements.txt
```

**Minimal installation** (without TensorFlow — uses HF or heuristic fallback):
```bash
pip install -r requirements-minimal.txt
```

### 4. (Optional) Configure Hugging Face Token

The token is pre-configured in `disease_detector.py`. To use your own:

```bash
# Set as environment variable
set HF_TOKEN=hf_your_token_here      # Windows
export HF_TOKEN=hf_your_token_here   # Linux/macOS
```

Or edit the `HF_TOKEN` variable directly in `disease_detector.py`.

---

## ▶️ Running the Application

```bash
python app.py
```

You will see:

```
==================================================
  AI-Powered Smart Farming Hub
  Dashboard: http://127.0.0.1:5000/
  Disease Detection: http://127.0.0.1:5000/disease
==================================================
```

Open your browser and navigate to:

| Page                 | URL                              |
| -------------------- | -------------------------------- |
| 🏠 **Dashboard**     | `http://127.0.0.1:5000/`        |
| 🔬 **Disease Detection** | `http://127.0.0.1:5000/disease` |
| 📜 **History**       | `http://127.0.0.1:5000/history` |

> **Note**: On first run, the Hugging Face models (~500 MB) and irrigation ML model will be downloaded/trained automatically. Subsequent runs are instant.

---

## 📡 API Reference

### `GET /api/sensor-data`
Returns current simulated sensor values with status indicators.

**Response:**
```json
{
  "temperature": 31.45,
  "humidity": 62.18,
  "temp_status": "warning",
  "humidity_status": "good",
  "irrigation_prediction": true,
  "irrigation_confidence": 0.87,
  "irrigation_status": "ON",
  "manual_mode": false,
  "timestamp": "2026-04-09 18:30:00"
}
```

---

### `POST /api/capture-and-detect`
Accepts a base64-encoded image (from browser webcam) or triggers OpenCV camera capture.

**Request Body:**
```json
{
  "image": "data:image/jpeg;base64,/9j/4AAQ...",
  "plant_name": "Tomato"
}
```

**Response:**
```json
{
  "success": true,
  "image_path": "/static/uploads/capture_20260409_183000.jpg",
  "crop": "Tomato",
  "disease": "Late Blight",
  "disease_name": "Late Blight",
  "confidence": 89.45,
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

### `POST /api/upload-and-detect`
Accepts a file upload via multipart form data.

**Request:** `multipart/form-data` with field `file`

**Response:** Same format as `/api/capture-and-detect`

---

### `GET /api/camera-status`
Check if camera hardware is available.

**Response:**
```json
{
  "available": true
}
```

---

### `POST /api/irrigation/toggle`
Toggle irrigation between auto and manual modes.

**Request Body:**
```json
{
  "mode": "manual",
  "status": "ON"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Irrigation set to MANUAL (ON)"
}
```

---

## 📸 Screenshots

| Dashboard | Disease Detection | History |
|-----------|-------------------|---------|
| Real-time sensor monitoring with irrigation status | Webcam capture and AI analysis interface | Chronological detection log with recommendations |

---

## ⚙ How It Works

### Disease Detection Pipeline

```
Image Input (Webcam / Upload)
        │
        ▼
┌─────────────────────┐
│  YOLOS-tiny Filter  │──── Human detected? → Reject ("Not a Plant")
└─────────┬───────────┘
          │ Plant image
          ▼
┌─────────────────────┐
│  MobileNetV2 (HF)   │──── Available? → Classify (38+ diseases)
└─────────┬───────────┘
          │ Not available
          ▼
┌─────────────────────┐
│  TFLite Model       │──── Available? → Local inference
└─────────┬───────────┘
          │ Not available
          ▼
┌─────────────────────┐
│  Color Heuristics   │──── Analyze green ratio, variance, spots
└─────────┬───────────┘
          │
          ▼
   Recommendation Engine → Store in SQLite → Return to UI
```

### Irrigation Prediction Logic

```
Temperature + Humidity + Hour of Day
        │
        ▼
┌──────────────────────────┐
│  Random Forest Classifier │
│  (100 estimators)         │
│                           │
│  Rules:                   │
│  ON if Temp > 32°C        │
│  ON if Temp > 28°C AND    │
│       Humidity < 50%      │
└───────────┬──────────────┘
            │
            ▼
   Prediction + Confidence → Dashboard UI
```

---

## 🔧️ Configuration

| Setting                | Location                 | Default                  |
| ---------------------- | ------------------------ | ------------------------ |
| Flask Secret Key       | `app.py`                 | `smart-farming-hub-2024` |
| Max Upload Size        | `app.py`                 | 16 MB                   |
| Server Port            | `app.py`                 | 5000                    |
| HF Model ID           | `disease_detector.py`    | `linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification` |
| HF Token              | `disease_detector.py`    | Pre-configured           |
| Temperature Range      | `sensors_simulator.py`   | 25.0 – 40.0 °C          |
| Humidity Range         | `sensors_simulator.py`   | 40.0 – 90.0 %           |
| Irrigation Threshold   | `irrigation_predictor.py`| Temp > 32°C or (>28°C & Humidity < 50%) |
| Database Path          | `database.py`            | `smart_farming.db`       |
| History Limit          | `database.py`            | 50 records               |

---

## 🧪 Testing

Run the test suite:

```bash
# Test API endpoints
python test_api.py

# Test file upload detection
python test_api_upload.py

# Test disease detection module
python test_detection.py

# Test Hugging Face integration
python test_hf.py

# Test non-leaf image rejection
python test_hf_non_leaf.py

# Test human detection rejection
python test_human.py
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Flask auto-reloader crashes** | Run with `python app.py` (not `flask run`). The reloader can conflict with PyTorch model loading. |
| **Models downloading slowly** | First run downloads ~500 MB of models. Ensure a stable internet connection. Subsequent runs are instant. |
| **Camera not detected** | Ensure no other app is using the webcam. Try closing video call apps. Use file upload as an alternative. |
| **TensorFlow import error on Python 3.13** | TensorFlow doesn't support Python 3.13 yet. The app falls back to HF/heuristic detection automatically. |
| **Out of memory** | PyTorch + Transformers require ~2 GB RAM. Close other memory-heavy applications. |
| **Low confidence results** | Ensure the leaf image is clear, well-lit, and fills most of the frame. Blurry or distant shots reduce accuracy. |

---

## 🔮 Future Enhancements

- [ ] Real IoT sensor integration (DHT11, Soil Moisture Sensor via Raspberry Pi GPIO)
- [ ] Multi-language support for recommendations (Hindi, Telugu, Tamil)
- [ ] Weather API integration for context-aware irrigation
- [ ] Progressive Web App (PWA) for mobile use in the field
- [ ] Export detection history as PDF/CSV reports
- [ ] Notification system (SMS/Email alerts for disease detection)
- [ ] Drone image support for large-scale field scanning
- [ ] Crop yield prediction based on historical disease data

---

## 📜 License

Academic project for educational purposes. Use freely for demonstration and research in smart agriculture.

---

## 👥 Contributors

- Abhilash and Team — B.Tech Major Project
 -Abhilash Bhandari
 -Abhishek PM
 -Annaraj Mulagund
 -Bharath C
- Built with ❤️ for smarter, sustainable agriculture

---

<p align="center">
  <b>🌱 LeafCare AI — Because every leaf tells a story.</b>
</p>
