# Customer Complaint Resolution API

FastAPI service for the Customer Complaint Resolution automation.

- POST `/api/v1/resolutions` creates or updates one record.
- `processedTime` is the unique API record key.
- `caseNumber` remains the business case identifier.
- GET `/api/v1/resolutions` returns the cumulative records.
- GET `/health` returns health status.
- Data is persisted in `data/resolutions.json`.

## Run on Windows

python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Swagger: http://localhost:8000/docs
