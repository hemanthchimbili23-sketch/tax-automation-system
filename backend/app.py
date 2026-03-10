from __future__ import annotations

import os
import sqlite3
from datetime import date, datetime, timedelta
from typing import Any

from flask import Flask, jsonify, request

MIN_TAX_YEAR = 2000
MAX_TAX_YEAR = 2100


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.getenv("DATABASE_PATH", os.path.join(app.root_path, "tax_automation.db")),
    )

    if test_config:
        app.config.update(test_config)

    def get_db() -> sqlite3.Connection:
        conn = sqlite3.connect(app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db() -> None:
        conn = get_db()
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    tax_year INTEGER NOT NULL,
                    income REAL NOT NULL,
                    deductions REAL NOT NULL,
                    estimated_tax REAL NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    record_id INTEGER NOT NULL,
                    deadline TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(record_id) REFERENCES records(id)
                )
                """
            )
        conn.close()

    def calculate_estimated_tax(income: float, deductions: float) -> float:
        taxable_income = max(income - deductions, 0)
        return round(taxable_income * 0.10, 2)

    def parse_iso_date(value: Any) -> date:
        if not isinstance(value, str):
            raise ValueError("must be a string in YYYY-MM-DD format")
        return date.fromisoformat(value)

    @app.get("/")
    def index() -> Any:
        return jsonify(
            {
                "service": "tax-automation-system",
                "message": "Automated income tax prep and reminder API",
                "endpoints": [
                    "GET /health",
                    "POST /records",
                    "GET /records/<id>",
                    "GET /records/<id>/summary",
                    "POST /reminders",
                    "GET /reminders/upcoming?days=7",
                ],
            }
        )

    @app.get("/health")
    def health() -> Any:
        return jsonify({"status": "ok", "date": date.today().isoformat()})

    @app.post("/records")
    def create_record() -> Any:
        payload = request.get_json(silent=True) or {}
        required = ["name", "email", "tax_year", "income", "deductions"]
        missing = [field for field in required if field not in payload]
        if missing:
            return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400

        name = str(payload["name"]).strip()
        email = str(payload["email"]).strip()
        if not name:
            return jsonify({"error": "name is required"}), 400
        if "@" not in email:
            return jsonify({"error": "email must be a valid email address"}), 400

        try:
            tax_year = int(payload["tax_year"])
            income = float(payload["income"])
            deductions = float(payload["deductions"])
        except (TypeError, ValueError):
            return jsonify({"error": "tax_year must be int; income/deductions must be numbers"}), 400

        if not (MIN_TAX_YEAR <= tax_year <= MAX_TAX_YEAR):
            return jsonify({"error": f"tax_year must be between {MIN_TAX_YEAR} and {MAX_TAX_YEAR}"}), 400
        if income < 0 or deductions < 0:
            return jsonify({"error": "income and deductions must be non-negative"}), 400

        estimated_tax = calculate_estimated_tax(income=income, deductions=deductions)
        conn = get_db()
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO records (name, email, tax_year, income, deductions, estimated_tax, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    email,
                    tax_year,
                    income,
                    deductions,
                    estimated_tax,
                    datetime.utcnow().isoformat(),
                ),
            )
            record_id = cursor.lastrowid
        conn.close()

        return jsonify({"id": record_id, "estimated_tax": estimated_tax}), 201

    @app.get("/records/<int:record_id>")
    def get_record(record_id: int) -> Any:
        conn = get_db()
        row = conn.execute("SELECT * FROM records WHERE id = ?", (record_id,)).fetchone()
        conn.close()

        if row is None:
            return jsonify({"error": "Record not found"}), 404

        return jsonify(dict(row))

    @app.get("/records/<int:record_id>/summary")
    def get_record_summary(record_id: int) -> Any:
        conn = get_db()
        row = conn.execute("SELECT * FROM records WHERE id = ?", (record_id,)).fetchone()
        conn.close()

        if row is None:
            return jsonify({"error": "Record not found"}), 404

        taxable_income = round(max(row["income"] - row["deductions"], 0), 2)
        summary = {
            "record_id": row["id"],
            "name": row["name"],
            "tax_year": row["tax_year"],
            "income": row["income"],
            "deductions": row["deductions"],
            "taxable_income": taxable_income,
            "estimated_tax": row["estimated_tax"],
            "note": "Estimate only. Not an official filing output.",
        }
        return jsonify(summary)

    @app.post("/reminders")
    def create_reminder() -> Any:
        payload = request.get_json(silent=True) or {}
        required = ["record_id", "deadline"]
        missing = [field for field in required if field not in payload]
        if missing:
            return jsonify({"error": f"Missing required field(s): {', '.join(missing)}"}), 400

        try:
            record_id = int(payload["record_id"])
            deadline = parse_iso_date(payload["deadline"])
        except (TypeError, ValueError):
            return jsonify({"error": "record_id must be int and deadline must be YYYY-MM-DD"}), 400

        conn = get_db()
        record = conn.execute("SELECT id FROM records WHERE id = ?", (record_id,)).fetchone()
        if record is None:
            conn.close()
            return jsonify({"error": "Record not found"}), 404

        message = str(payload.get("message", f"Tax deadline is coming on {deadline.isoformat()}"))
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO reminders (record_id, deadline, message, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (record_id, deadline.isoformat(), message, datetime.utcnow().isoformat()),
            )
        conn.close()

        return jsonify({"id": cursor.lastrowid, "record_id": record_id, "deadline": deadline.isoformat()}), 201

    @app.get("/reminders/upcoming")
    def upcoming_reminders() -> Any:
        days_param = request.args.get("days", "7")
        try:
            days = int(days_param)
        except ValueError:
            return jsonify({"error": "days must be an integer"}), 400

        if days < 0:
            return jsonify({"error": "days must be non-negative"}), 400

        start = date.today()
        end = start + timedelta(days=days)

        conn = get_db()
        rows = conn.execute(
            """
            SELECT * FROM reminders
            WHERE deadline BETWEEN ? AND ?
            ORDER BY deadline ASC
            """,
            (start.isoformat(), end.isoformat()),
        ).fetchall()
        conn.close()

        return jsonify([dict(row) for row in rows])

    with app.app_context():
        init_db()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
