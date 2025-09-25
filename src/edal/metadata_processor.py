import logging

class MetadataProcessor:
    def normalize(self, obj: dict):
        """Extract metadata only, no raw payload"""
        logging.debug(f"Normalizing object metadata: {obj}")
        return {
            "timestamp": obj["timestamp"],
            "host": obj["host"],
            "event": obj["event"],
            "metric": obj["metric"]
        }

    def detect_anomaly(self, metric: float, threshold: float):
        logging.debug(f"Detecting anomaly for metric '{metric}' with threshold {threshold}.")
        return metric > threshold
