# Automated Income Tax Preparation & Reminder System

## Overview
Filing income tax is confusing for many people, especially when it comes to
organizing income details, deductions, and remembering important deadlines.
This project provides a lightweight Flask API that automates the basic workflow
for collecting records, estimating tax, and tracking reminders.

## Features
- Create tax records with income + deduction details
- Estimate tax using a simple 10% taxable-income rule (demo only)
- Generate a tax summary for each saved record
- Create and query upcoming reminder entries
- Run locally with Python or Docker

## Project Structure
```text
backend/
  app.py              # Flask app + SQLite initialization
  requirements.txt    # Python dependencies
  tests/test_app.py   # API test cases
Dockerfile
docker-compose.yml
README.md
```

## Quickstart (Local)
1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Run the API:
   ```bash
   python backend/app.py
   ```
4. Open `http://localhost:5000/health`.

## Quickstart (Docker)
```bash
docker compose up --build
```
API will be available on `http://localhost:5000`.

## Example API calls
Create a record:
```bash
curl -X POST http://localhost:5000/records \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice",
    "email": "alice@example.com",
    "tax_year": 2025,
    "income": 100000,
    "deductions": 20000
  }'
```

Get summary:
```bash
curl http://localhost:5000/records/1/summary
```

Create reminder:
```bash
curl -X POST http://localhost:5000/reminders \
  -H "Content-Type: application/json" \
  -d '{"record_id": 1, "deadline": "2026-04-10"}'
```

## Run tests
```bash
cd backend
python -m unittest -v
```

## Disclaimer
This project is for educational and demonstration purposes only.
It is not legal or tax advice and does not perform official government filing.
