FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY backend /app/backend

ENV PYTHONUNBUFFERED=1
ENV DATABASE_PATH=/app/backend/tax_automation.db

EXPOSE 5000

CMD ["python", "backend/app.py"]
