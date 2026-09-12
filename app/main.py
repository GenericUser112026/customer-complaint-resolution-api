from pathlib import Path
import json
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "resolutions.json"

app = FastAPI(
    title="Customer Complaint Resolution API",
    version="1.2.0",
    description="Cumulative Customer Complaint Resolution API. Processed Time is the unique record key."
)


class ResolutionRecord(BaseModel):
    """Final complaint-resolution record sent by Automation Anywhere."""

    caseNumber: str = Field(..., min_length=1)
    customerName: str = ""
    customerEmail: str = ""
    orderNumber: str = ""
    resolutionStatus: str = ""
    nextAction: str = ""
    overridden: str = ""
    comments: str = ""
    caseStatus: str = ""
    processedTime: str = Field(..., min_length=1)


def load_records() -> List[dict]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")
    try:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
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
    return {
        "status": "healthy",
        "service": "customer-complaint-resolution-api",
        "version": "1.2.0",
    }


@app.post("/api/v1/resolutions")
def upsert_resolution(record: ResolutionRecord):
    """Create a new record or update the existing record with the same processedTime."""
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
                "record": payload,
            }

    records.append(payload)
    save_records(records)
    return {
        "success": True,
        "operation": "created",
        "uniqueKey": record.processedTime,
        "totalRecords": len(records),
        "record": payload,
    }


@app.get("/api/v1/resolutions")
def get_resolutions():
    records = load_records()
    return {
        "success": True,
        "totalRecords": len(records),
        "records": records,
    }


@app.get("/results", response_class=HTMLResponse)
def published_results():
    """Human-friendly public page showing all cumulative published results."""
    records = load_records()

    columns = [
        ("caseNumber", "Case Number"),
        ("customerName", "Customer Name"),
        ("customerEmail", "Customer Email"),
        ("orderNumber", "Order Number"),
        ("resolutionStatus", "Resolution Status"),
        ("nextAction", "Next Action"),
        ("overridden", "Overridden"),
        ("comments", "Comments"),
        ("caseStatus", "Case Status"),
        ("processedTime", "Processed Time"),
    ]

    def esc(value):
        import html
        return html.escape(str(value if value is not None else ""))

    headers = "".join(f"<th>{esc(label)}</th>" for _, label in columns)
    rows = []
    for record in records:
        cells = "".join(f"<td>{esc(record.get(key, ""))}</td>" for key, _ in columns)
        rows.append(f"<tr>{cells}</tr>")

    table_body = "".join(rows) if rows else '<tr><td colspan="10" class="empty">No published results yet.</td></tr>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Customer Complaint Resolution - Published Results</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 0; background: #f4f6f8; color: #1f2937; }}
.container {{ max-width: 1600px; margin: 0 auto; padding: 32px 20px; }}
h1 {{ margin: 0 0 8px; font-size: 30px; }}
.subtitle {{ margin: 0 0 24px; color: #6b7280; }}
.summary {{ display: inline-block; background: white; border: 1px solid #e5e7eb; border-radius: 10px; padding: 12px 18px; margin-bottom: 20px; font-weight: 600; }}
.table-wrap {{ background: white; border: 1px solid #e5e7eb; border-radius: 10px; overflow: auto; box-shadow: 0 2px 8px rgba(0,0,0,.05); }}
table {{ border-collapse: collapse; width: 100%; min-width: 1200px; }}
th, td {{ padding: 12px 14px; border-bottom: 1px solid #e5e7eb; text-align: left; white-space: nowrap; font-size: 14px; }}
th {{ background: #111827; color: white; position: sticky; top: 0; }}
tr:hover td {{ background: #f9fafb; }}
.empty {{ text-align: center; padding: 30px; color: #6b7280; }}
.footer {{ margin-top: 16px; color: #6b7280; font-size: 13px; }}
</style>
</head>
<body>
<div class="container">
<h1>Customer Complaint Resolution — Published Results</h1>
<p class="subtitle">Complete cumulative results published by the Customer Complaint Resolution system.</p>
<div class="summary">Total Published Records: {len(records)}</div>
<div class="table-wrap">
<table>
<thead><tr>{headers}</tr></thead>
<tbody>{table_body}</tbody>
</table>
</div>
<p class="footer">This page displays the current cumulative published results.</p>
</div>
</body>
</html>"""


@app.get("/api/v1/resolutions/{processed_time:path}")
def get_resolution(processed_time: str):
    for record in load_records():
        if record.get("processedTime") == processed_time:
            return {"success": True, "record": record}
    raise HTTPException(status_code=404, detail="Resolution record not found")
