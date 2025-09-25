import aioboto3
import logging
from datetime import datetime, timedelta, timezone
from .config import settings
import json

class S3Fetcher:
    def __init__(self):
        self.bucket = settings.s3_bucket
        self.endpoint = settings.aws_endpoint
        self.session = aioboto3.Session()

    async def fetch_recent_objects(self):
        """Fetch objects modified in last X minutes"""
        logging.info(f"Fetching recent objects from S3 bucket '{self.bucket}'.")
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=settings.incremental_minutes)
        async with self.session.client("s3", endpoint_url=self.endpoint) as s3:
            resp = await s3.list_objects_v2(Bucket=self.bucket)
            objs = resp.get("Contents", [])
            keys = []
            for o in objs:
                if o["LastModified"] >= cutoff:
                    keys.append(o["Key"])
            logging.info(f"Found {len(keys)} recent objects in S3 bucket '{self.bucket}'.")
            return keys

    async def read_object(self, key):
        logging.debug(f"Reading object '{key}' from S3 bucket '{self.bucket}'.")
        async with self.session.client("s3", endpoint_url=self.endpoint) as s3:
            obj = await s3.get_object(Bucket=self.bucket, Key=key)
            body = await obj["Body"].read()
            logging.debug(f"Object '{key}' read and loaded from S3.")
            return json.loads(body)
