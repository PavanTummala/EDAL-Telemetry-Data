import logging
from sklearn.ensemble import IsolationForest
import numpy as np

class MetadataProcessor:
    def __init__(self):
        # For demo: train on normal metrics in range [0, threshold]
        self.model = IsolationForest(contamination=0.05, random_state=42)
        # Assume normal metrics are between 0 and threshold
        self.is_trained = False
        self.threshold = None

    def train(self, metrics, threshold):
        # metrics: list of float
        self.model.fit(np.array(metrics).reshape(-1, 1))
        self.is_trained = True
        self.threshold = threshold
        logging.info(f"IsolationForest trained on {len(metrics)} samples.")

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
        logging.debug(f"Detecting anomaly for metric '{metric}' using IsolationForest ML model.")
        if not self.is_trained:
            # Fallback to threshold if not trained
            logging.warning("IsolationForest not trained, using threshold fallback.")
            return metric > threshold
        pred = self.model.predict(np.array([[metric]]))
        # IsolationForest returns -1 for anomaly, 1 for normal
        return pred[0] == -1
