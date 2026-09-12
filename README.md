# Customer Complaint Resolution API

FastAPI service for receiving the final Customer Complaint Resolution record from Automation Anywhere.

## API behavior

- `GET /health` — health check
- `POST /api/v1/resolutions` — create or update a resolution record
- `GET /api/v1/resolutions` — return all cumulative records
- `GET /api/v1/resolutions/{processed_time}` — return one record

## Unique key / idempotency

`processedTime` is the unique record key. Posting the same `processedTime` again updates the existing record instead of creating a duplicate.

This supports the intended cumulative behavior:

- Run 1 → 2 records
- Run 2 → 5 records total
- Run 3 → 10 records total

## Payload

```json
{
  "caseNumber": "Case4_ORD-10002",
  "customerName": "Adam",
  "customerEmail": "genericmail112026@gmail.com",
  "orderNumber": "ORD-10002",
  "resolutionStatus": "APPROVED",
  "nextAction": "REPLACEMENT",
  "overridden": "No",
  "comments": "",
  "caseStatus": "Processed",
  "processedTime": "2026-09-11T16:03:31"
}
```

## Run locally

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then open:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

## Deployment

The repository can be deployed to a public HTTPS web-service host such as Render. The service must run:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

The public endpoint used by Automation Anywhere API Task should be:

```text
https://<public-host>/api/v1/resolutions
```

## Important persistence note

The current JSON file store is suitable for demonstration/testing. On hosting platforms with ephemeral local disks, records can be lost after a restart or redeploy. For production cumulative storage, replace the JSON file with a persistent database.
