# EDAL POC – Ephemeral Data Access Layer (BugRaid.AI)

This repo implements a Proof-of-Concept **EDAL** service for telemetry ingestion, anomaly detection, and AI-driven incident response.

---

## Features
- Synthetic MELT data stored in **LocalStack S3**
- **Incremental fetch** (last 15 minutes only)
- **Metadata-only processing** (no raw logs leave S3)
- **Watermarks** tracked in MongoDB:
  - Object-level
  - Bucket-level
- **Signals emitted to Kinesis** (with retry + fallback to SQS)
- **Stateless / ephemeral** containerized design
- **Deduplication** documented & implemented
- Async Python (`aioboto3`, `motor`)
- Dockerized service
- Full test suite with `pytest`

---

## Setup

```bash
# Clone repo
git clone https://github.com/<your-username>/edal-poc.git
cd edal-poc

# Start infra (LocalStack + MongoDB + EDAL service)
docker-compose up --build

# Initialize LocalStack resources
docker-compose run --rm edal-service python scripts/setup_localstack.py

# Generate synthetic test data
docker-compose run --rm edal-service python scripts/generate_test_data.py

# Run EDAL processor
docker-compose run --rm edal-service python -m src.edal.main

# Run tests
docker-compose run --rm edal-service pytest -v
```

## Deduplication

Each processed S3 object is tracked by:

Bucket + ObjectKey + MD5 hash

Stored in MongoDB watermark collection

Before processing, EDAL checks if the hash matches the stored value
→ If yes, skip (duplicate object)
→ If no, process and update watermark

This guarantees no duplicate signals even if the same file is re-uploaded.

## Acceptance Criteria

Processes 1GB in <5 min (tested with synthetic data batches)

No raw logs leave LocalStack

Watermarks updated correctly

Signals published to Kinesis with evidence pointers
