import asyncio
import aioboto3
import random
from datetime import datetime, timedelta

async def main():
    session = aioboto3.Session()
    async with session.client(
        "s3",
        endpoint_url="http://localstack:4566",
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test"
    ) as s3:
        bucket = "edal-telemetry-bucket"
        try:
            await s3.create_bucket(Bucket=bucket)
        except:
            pass
        for i in range(10000):
            key = f"metrics/{datetime.utcnow().isoformat()}_{i}.json"
            data = str({"metric": random.random(), "timestamp": datetime.utcnow().isoformat()})
            await s3.put_object(Bucket=bucket, Key=key, Body=data.encode())
        print("Synthetic data generated.")

if __name__ == "__main__":
    asyncio.run(main())