import asyncio, hashlib, logging, time
from .s3_fetcher import S3Fetcher
from .metadata_processor import MetadataProcessor
from .watermark import WatermarkStore
from .signal_emitter import SignalEmitter
from .config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

async def main():
    logging.info("EDAL pipeline started.")
    start_time = time.time()
    fetcher = S3Fetcher()
    processor = MetadataProcessor()
    wm = WatermarkStore()
    emitter = SignalEmitter()

    # Step 1: Fetch initial batch and train anomaly model
    keys = await fetcher.fetch_recent_objects()
    logging.info(f"Fetched {len(keys)} objects from S3 bucket '{settings.s3_bucket}'.")
    initial_metrics = []
    initial_batch_size = min(50, len(keys))  # Use up to 50 objects for training
    for key in keys[:initial_batch_size]:
        obj = await fetcher.read_object(key)
        norm = processor.normalize(obj)
        initial_metrics.append(norm["metric"])
    if initial_metrics:
        processor.train(initial_metrics, settings.anomaly_threshold)
        logging.info(f"Trained anomaly detection model on {len(initial_metrics)} metrics.")
    else:
        logging.warning("No metrics available for anomaly model training.")

    # Step 2: Main processing loop
    processed_count = 0
    deduped_count = 0
    anomaly_count = 0
    for key in keys:
        try:
            obj = await fetcher.read_object(key)
            logging.debug(f"Read object '{key}' from S3.")
            norm = processor.normalize(obj)
            logging.debug(f"Normalized metadata for object '{key}'.")

            # Deduplication check
            md5 = hashlib.md5(str(norm).encode()).hexdigest()
            prev = await wm.get_object_watermark(settings.s3_bucket, key)
            if prev and prev.get("md5") == md5:
                logging.info(f"Duplicate detected for object '{key}', skipping.")
                deduped_count += 1
                continue

            if processor.detect_anomaly(norm["metric"], settings.anomaly_threshold):
                anomaly_count += 1
                signal = {
                    "bucket": settings.s3_bucket,
                    "object": key,
                    "metadata": norm,
                    "evidence_md5": md5
                }
                await emitter.emit(signal)
                logging.info(f"Anomaly detected and signal emitted for object '{key}'.")

            await wm.update_object_watermark(settings.s3_bucket, key, md5)
            logging.debug(f"Updated watermark for object '{key}'.")
            processed_count += 1
        except Exception as e:
            logging.error(f"Error processing object '{key}': {e}")

    await wm.update_bucket_watermark(settings.s3_bucket)
    logging.info(f"Updated bucket watermark for '{settings.s3_bucket}'.")
    elapsed = time.time() - start_time
    logging.info(f"EDAL pipeline completed. Processed: {processed_count}, Deduped: {deduped_count}, Anomalies: {anomaly_count}, Time: {elapsed:.2f}s.")

if __name__ == "__main__":
    asyncio.run(main())
