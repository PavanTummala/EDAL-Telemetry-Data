import aioboto3, hashlib, json, asyncio
from .config import settings

import logging

class SignalEmitter:
    def __init__(self):
        self.session = aioboto3.Session()

    async def emit(self, payload: dict):
        """Try to send to Kinesis, fallback to SQS"""
        logging.info(f"Emitting signal for object '{payload.get('object')}' in bucket '{payload.get('bucket')}'.")
        data = json.dumps(payload)
        partition_key = payload.get("host") or payload.get("metadata", {}).get("host") or "default"
        async with self.session.client("kinesis", endpoint_url=settings.aws_endpoint) as k:
            try:
                await k.put_record(StreamName=settings.kinesis_stream,
                                   Data=data,
                                   PartitionKey=partition_key)
                logging.info(f"Signal sent to Kinesis for object '{payload.get('object')}'.")
            except Exception as e:
                logging.warning(f"Kinesis failed: {e}, falling back to SQS for object '{payload.get('object')}'.")
                async with self.session.client("sqs", endpoint_url=settings.aws_endpoint) as sqs:
                    url = await sqs.get_queue_url(QueueName=settings.sqs_queue)
                    await sqs.send_message(QueueUrl=url["QueueUrl"], MessageBody=data)
                    logging.info(f"Signal sent to SQS for object '{payload.get('object')}'.")
