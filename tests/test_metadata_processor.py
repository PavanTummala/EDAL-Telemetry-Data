import pytest
from src.edal.metadata_processor import MetadataProcessor

def test_normalize_extracts_metadata():
    p = MetadataProcessor()
    raw = {"timestamp":"2023-01-01","host":"h","event":"cpu","metric":0.9,"raw":"xxx"}
    norm = p.normalize(raw)
    assert "raw" not in norm
    assert "metric" in norm
    assert norm["host"] == "h"

def test_detect_anomaly():
    p = MetadataProcessor()
    assert p.detect_anomaly(0.9,0.8) is True
    assert p.detect_anomaly(0.5,0.8) is False
