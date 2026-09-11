from pathlib import Path
import json
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "resolutions.json"

app = FastAPI(
    title="Customer Complaint Resolution API",
    version="1.0.0",
    description="Cumulative API using Processed Time as the unique record key."
)

class ResolutionRecord(BaseModel):
    processedTime: str = Field(..., min_length=1)
    caseNumber: str = Field(..., min_length=1)
    customerName: str = ""
    customerEmail: str = ""
    orderNumber: str = ""
    resolutionStatus: str = ""
    overridden: str = ""
    comments: str = ""
    caseStatus: str = ""

def load_records() -> List[dict]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

def save_records(records: List[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

@app.get("/health")
def health():
    return {"status": "healthy", "service": "customer-complaint-resolution-api"}

@app.post("/api/v1/resolutions")
def upsert_resolution(record: ResolutionRecord):
    records = load_records()
    payload = record.model_dump()

    for i, existing in enumerate(records):
        if existing.get("processedTime") == record.processedTime:
            records[i] = payload
            save_records(records)
            return {
                "success": True,
                "operation": "updated",
                "uniqueKey": record.processedTime,
                "totalRecords": len(records),
                "record": payload
            }

    records.append(payload)
    save_records(records)
    return {
        "success": True,
        "operation": "created",
        "uniqueKey": record.processedTime,
        "totalRecords": len(records),
        "record": payload
    }

@app.get("/api/v1/resolutions")
def get_resolutions():
    records = load_records()
    return {"success": True, "totalRecords": len(records), "records": records}

@app.get("/api/v1/resolutions/{processed_time:path}")
def get_resolution(processed_time: str):
    for record in load_records():
        if record.get("processedTime") == processed_time:
            return {"success": True, "record": record}
    raise HTTPException(status_code=404, detail="Resolution record not found")
