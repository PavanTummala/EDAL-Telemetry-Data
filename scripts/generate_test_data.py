import boto3, json, random, time, os
from datetime import datetime, timedelta, timezone

bucket = os.getenv("S3_BUCKET", "telemetry-bucket")
s3 = boto3.client("s3", endpoint_url="http://localstack:4566")

def generate_obj(minutes_ago):
    ts = datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)
    return {
        "timestamp": ts.isoformat(),
        "host": f"host-{random.randint(1,5)}",
        "event": random.choice(["cpu_usage", "mem_usage", "disk_io", "net_latency"]),
        "metric": random.random()
    }

def main():
    for i in range(50):
        obj = generate_obj(random.randint(0, 30))
        key = f"telemetry/{int(time.time()*1000)}_{i}.json"
        s3.put_object(Bucket=bucket, Key=key, Body=json.dumps(obj))
        print(f"Uploaded {key}")

if __name__ == "__main__":
    main()
