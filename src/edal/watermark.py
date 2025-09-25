from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from .config import settings

import logging

class WatermarkStore:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.mongo_uri)
        self.collection = self.client.edal.watermarks

    async def update_object_watermark(self, bucket, key, md5):
        logging.info(f"Updating watermark for object '{key}' in bucket '{bucket}'.")
        await self.collection.update_one(
            {"bucket": bucket, "object": key},
            {"$set": {
                "last_processed": datetime.now(timezone.utc).isoformat(),
                "md5": md5
            }},
            upsert=True
        )

    async def get_object_watermark(self, bucket, key):
        logging.debug(f"Getting watermark for object '{key}' in bucket '{bucket}'.")
        return await self.collection.find_one({"bucket": bucket, "object": key})

    async def update_bucket_watermark(self, bucket):
        logging.info(f"Updating bucket watermark for '{bucket}'.")
        await self.collection.update_one(
            {"bucket": bucket, "object": "__bucket__"},
            {"$set": {"last_processed": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )
