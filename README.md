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

## Logic 

This project is built on a stateless,Polling based streaming-first architecture. The core idea is to treat the EDAL service as an ephemeral processing layer that analyzes data in-flight without needing to store the raw telemetry itself.

**Key principles of this approach include:**

Externalized State: While the processing container is stateless, its progress is tracked externally in MongoDB. This watermarking system allows any instance of the service to know exactly what data has already been processed, enabling robust and scalable deployments.

Metadata-Only Processing: To enhance security and minimize data transfer, the service is designed to only fetch and analyze object metadata. Raw logs and payloads never leave the S3 data store.

Asynchronous Operations: The entire pipeline is built with asyncio, using libraries like aioboto3 and motor. This makes the service highly efficient at handling I/O-bound tasks like fetching from S3, querying MongoDB, and publishing to Kinesis, allowing for high concurrency.

Resilient Signal Emission: The system is designed to be fault-tolerant. If a signal cannot be published to Kinesis, it will automatically retry and has a fallback mechanism to send the signal to an SQS queue, ensuring no anomalies are ever lost.

**ML Anomaly Detection**

Anomaly detection is the core intelligent component of the EDAL service. The goal is to identify unusual or unexpected patterns in the telemetry data that could signify an issue.

Model: We use IsolationForest, an efficient, unsupervised machine learning algorithm. It's well-suited for this use case because it excels at identifying outliers without requiring pre-labeled training data.

**Process:**

Dynamic Training: The model is not static. At the beginning of each run, it fetches a small, recent batch of objects from S3.

Baseline Creation: It assumes this initial batch represents "normal" operational behavior and trains the IsolationForest model on the metrics extracted from this data.

Inference: For each new, unique telemetry object that is processed, its metric is fed to the trained model. The model then classifies it as either an anomaly or normal. If identified as an anomaly, a signal is emitted.

Assumptions: Instead of continous emitting, emit only certain metric in metadata is seen as threshold, but this is tested on continous emission also.








