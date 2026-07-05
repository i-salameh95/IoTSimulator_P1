# Smart Home IoT Simulator – Phase 1

---

## 1. Executive Summary

- **Scope**: Phase‑1 Smart Home simulator with three sensors (temperature, light, motion), three actuators (fan, light, alarm), and a rule-based controller.
- **Features**: simulation cycles, historical queries, actuator monitoring, centralized logging, CSV fallback storage, Dockerized deployment, React dashboard.
- **Data Flow**: Sensors → Simulation Engine → Controller → MongoDB (or CSV) → REST API → React dashboard.
- **Why it matters**: Demonstrates IoT principles (data acquisition, decision making, actuation, visualization) with production tooling that can later evolve toward real devices and AI logic.

---

## 2. Architecture at a Glance

```
IoT Devices (simulated) ─┐
                          │ sensor data
                    ┌──────▼──────┐
                    │ Sensor      │  Temperature 15‑40°C
                    │ Simulator   │  Light 0‑100
                    └──────┬──────┘  Motion 0/1
                           │
                    ┌──────▼─────────────┐    MongoDB (phase‑1 storage)
                    │ Simulation Engine  │─── sensor_readings
                    │  + Controller      │─── actuator_states
                    └──────┬─────────────┘─── logs
                           │
                    ┌──────▼──────┐                CSV fallback
                    │ FastAPI API │──────────────► backend/storage/*.csv
                    └──────┬──────┘
                           │ HTTP/JSON
                    ┌──────▼──────┐
                    │ React UI    │
                    │  (Dashboard)│
                    └─────────────┘
```

---

## 3. Technology Stack

| Layer        | Technology                                                    |
| ------------ | -------------------------------------------------------------- |
| Backend      | Python 3.11+/FastAPI, Pydantic, Uvicorn                        |
| Storage      | MongoDB (primary), UTF‑8 CSV fallback (sensor/actuator/logs)   |
| Frontend     | React 18, Axios, Recharts, CRA tooling                         |
| Tooling      | Docker Compose, Node 18, npm, curl/Postman                     |

---

## 4. Repository Layout

```text
IoTSimulator_P1/
├── backend/
│   ├── app/
│   │   ├── api/                # sensors, actuators, simulation, logs routers
│   │   ├── core/               # config, Mongo/CSV services, logger
│   │   ├── models/             # Pydantic schemas
│   │   ├── services/           # sensor simulator, controller, engine
│   │   └── main.py             # FastAPI entry point
│   ├── storage/                # CSV fallback output (generated)
│   ├── scripts/                # Utility helpers (e.g., data generation)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # Dashboard, charts, actuator + logs panels
│   │   ├── services/           # Axios API client
│   │   └── App.js
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml          # Backend + frontend + MongoDB stack
├── Project_Phase#1.pdf         # Assignment brief
└── README.md                   # This document
```

---

## 5. Core Building Blocks

### 5.1 Sensor Simulator (`services/simulator.py`)
- Generates readings for each device (`smart_home_001..003`) across three measurements.
- Temperature 15‑40 °C, Light 0‑100, Motion {0,1} with timestamps/tags.

### 5.2 Simulation Engine (`services/simulation_engine.py`)
1. Pull readings for every device.
2. Persist to MongoDB or CSV via `MongoDBService` (auto fallback when Mongo is offline).
3. Invoke the controller to evaluate rules.
4. Store actuator responses + logs.
5. Repeat for N cycles with optional delay.

### 5.3 Controller & Rules (`services/actuator_controller.py`)
- **Rule 1**: `temperature > 30°C → fan = ON` else OFF.
- **Rule 2**: `motion == 1 AND light < 20 → light = ON` else OFF.
- **Rule 3**: `motion == 1 AND temperature ≥ 37°C → alarm = ON` else OFF.
- Keeps in-memory actuator states and records transitions for history endpoints.

### 5.4 Logging & Storage (`core/logger.py`, `core/mongodb_client.py`, `core/csv_storage.py`)
- Unified logging API writes to MongoDB when available, otherwise to `backend/storage/logs.csv` using UTF‑8.
- Sensor/actuator data follow the same pattern (`sensor_readings.csv`, `actuator_states.csv`).

### 5.5 Frontend Dashboard (`frontend/src/components`)
- **SimulationControl** runs single or multi-cycle jobs.
- **ActuatorStatus** polls current actuator states.
- **LogsDisplay** auto-refreshes controller/sensor logs with filters.
- **SensorChart** visualizes historical data via Recharts.

---

## 6. Operating Modes (How to Run)

### Option A – Docker Compose (full stack)
```bash
cp .env.example .env          # Windows: copy .env.example .env
# Edit .env and choose local-only credentials.
docker compose up -d
docker compose ps             # verify all services are Up
```
Services exposed:
- Frontend: http://localhost:3000
- Backend/API docs: http://localhost:8000/docs
- Mongo Express: http://localhost:8081 (credentials from `.env`)

### Option B – Local dev with CSV fallback (no Docker required)
**Backend**
```bash
cd backend
py -3.12 -m venv .venv && .venv\Scripts\activate  # or python3 -m venv on Linux/macOS
pip install -r requirements.txt
uvicorn app.main:app --reload --port 9000
```
(No MongoDB → automatic CSV mode. Files appear under `backend/storage/`.)

**Frontend**
```bash
cd frontend
npm install
REACT_APP_API_URL=http://localhost:9000 npm start   # or set in .env
```

**Generate data**: trigger `POST /api/v1/simulation/run-cycle` or use the dashboard buttons. Inspect `backend/storage/{sensor_readings,actuator_states,logs}.csv` for results.

---

## 7. API Quick Reference

| Endpoint | Description |
| --- | --- |
| `POST /api/v1/simulation/run-cycle` | One full cycle (sensors → controller → actuators). |
| `POST /api/v1/simulation/run?num_cycles=N&delay_seconds=S` | Batch cycles with delay. |
| `POST /api/v1/sensors/ingest` | Manually push a reading (for tests or integrations). |
| `POST /api/v1/sensors/ingest/batch` | Push multiple readings at once. |
| `POST /api/v1/sensors/query/historical` | Historical data (supports measurement/device filters). |
| `POST /api/v1/sensors/query/aggregated` | Windowed aggregations (`mean/max/min/sum`). |
| `GET /api/v1/sensors/measurements` | Available measurement types. |
| `GET /api/v1/sensors/devices` | Known device IDs. |
| `GET /api/v1/actuators/states` | Full actuator history (chronological). |
| `GET /api/v1/actuators/states/current` | Latest state per actuator. |
| `POST /api/v1/actuators/control` | Manually set an actuator state. |
| `GET /api/v1/logs/` | System logs with level/source/device filters. |

*When running in CSV mode, these endpoints read/write the CSV files transparently.*

---

## 8. Dashboard Walkthrough

1. **Simulation Control** – choose single cycle or multi-cycle (default 20) and watch status messages.
2. **Actuator Status** – displays Fan/Light/Alarm states per device, auto-refreshing every 2 seconds.
3. **System Logs** – streaming log view with filters for level and source.
4. **Sensor Chart** – select temperature/light/motion and plot recent readings; refresh button fetches latest data.

---

## 9. Data Outputs & Fallback Files

| File | Purpose |
| --- | --- |
| `backend/storage/sensor_readings.csv` | All simulated readings with timestamps/device IDs. |
| `backend/storage/actuator_states.csv` | Chronological actuator transitions. |
| `backend/storage/logs.csv` | Info/Warn/Error entries from sensors, controller, simulation engine. |

Delete these files to start fresh; the backend will recreate them automatically.

---

## 10. Development Notes & Future Work

- **Future ideas**: integrate real devices over MQTT, add background rule evaluation and analytics, add AI-driven decision modules, and support physical actuator overrides.
- **Testing**: no automated tests yet; validate via the API docs (`/docs`) or the dashboard, and add unit/API tests as needed.
- **Performance**: MongoDB indexes cover measurement/device/sensor queries; the aggregation endpoint provides windowed summaries.

---

## 11. Support / References

- API docs live at `/docs` (Swagger UI) once the backend is running.
- Mongo Express credentials are read from `.env`; do not commit that file.
- For CSV mode troubleshooting: ensure UTF‑8 CSV files and delete stale ANSI files if the logger endpoints raise encoding errors.

---

Happy simulating!
