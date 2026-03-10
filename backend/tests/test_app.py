from datetime import date, timedelta
import tempfile
import unittest

from app import create_app


class TaxAutomationAPITest(unittest.TestCase):
    def setUp(self):
        self.db_file = tempfile.NamedTemporaryFile(suffix=".db")
        self.app = create_app({"TESTING": True, "DATABASE": self.db_file.name})
        self.client = self.app.test_client()

    def tearDown(self):
        self.db_file.close()

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_create_record_and_get_summary(self):
        create_response = self.client.post(
            "/records",
            json={
                "name": "Alice",
                "email": "alice@example.com",
                "tax_year": 2025,
                "income": 100000,
                "deductions": 20000,
            },
        )
        self.assertEqual(create_response.status_code, 201)
        record_id = create_response.get_json()["id"]

        summary_response = self.client.get(f"/records/{record_id}/summary")
        self.assertEqual(summary_response.status_code, 200)
        summary = summary_response.get_json()
        self.assertEqual(summary["taxable_income"], 80000)
        self.assertEqual(summary["estimated_tax"], 8000)

    def test_create_and_fetch_upcoming_reminder(self):
        create_response = self.client.post(
            "/records",
            json={
                "name": "Bob",
                "email": "bob@example.com",
                "tax_year": 2025,
                "income": 60000,
                "deductions": 10000,
            },
        )
        record_id = create_response.get_json()["id"]
        deadline = (date.today() + timedelta(days=30)).isoformat()

        reminder_response = self.client.post(
            "/reminders",
            json={"record_id": record_id, "deadline": deadline},
        )
        self.assertEqual(reminder_response.status_code, 201)

        upcoming_response = self.client.get("/reminders/upcoming?days=60")
        self.assertEqual(upcoming_response.status_code, 200)
        reminders = upcoming_response.get_json()
        self.assertGreaterEqual(len(reminders), 1)

    def test_invalid_email_returns_400(self):
        response = self.client.post(
            "/records",
            json={
                "name": "NoEmail",
                "email": "not-an-email",
                "tax_year": 2025,
                "income": 25000,
                "deductions": 5000,
            },
        )
        self.assertEqual(response.status_code, 400)

    def test_invalid_tax_year_returns_400(self):
        response = self.client.post(
            "/records",
            json={
                "name": "Future",
                "email": "future@example.com",
                "tax_year": 3000,
                "income": 25000,
                "deductions": 5000,
            },
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
