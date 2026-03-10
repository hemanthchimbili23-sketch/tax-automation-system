# Automated Income Tax Preparation & Reminder System

## Overview
This project now includes a **real local frontend app** plus a Flask API backend.
You can run the UI locally first, then connect it to the backend API.

## Stack
- Frontend: HTML, CSS, Vanilla JavaScript (`frontend/`)
- Backend: Python Flask + SQLite (`backend/`)
- Containerization: Docker + docker compose

## Project Structure
```text
frontend/
  index.html
  styles.css
  app.js
backend/
  app.py
  requirements.txt
  tests/test_app.py
Dockerfile
docker-compose.yml
README.md
```

## Run locally (frontend first)
1. Start frontend static server:
   ```bash
   cd frontend
   python -m http.server 5500
   ```
2. Open `http://localhost:5500`.

This allows you to see and use the app UI locally immediately.

## Run backend API locally
In a new terminal:
```bash
pip install -r backend/requirements.txt
python backend/app.py
```
Backend runs at `http://localhost:5000`.

In the frontend UI, keep API base URL as `http://localhost:5000`.

## What the frontend can do
- Create tax records
- Fetch record summary by record ID
- Create reminders
- Query upcoming reminders

## API quick checks (optional)
```bash
curl http://localhost:5000/health
```

## Run tests
```bash
cd backend
python -m unittest -v
```

## Docker run
```bash
docker compose up --build
```

## Disclaimer
Educational/demo project only. Not legal or tax advice.
