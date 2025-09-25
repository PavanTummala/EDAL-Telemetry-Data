from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    aws_endpoint: str = "http://localstack:4566"
    region: str = "us-east-1"
    s3_bucket: str = "telemetry-bucket"
    kinesis_stream: str = "telemetry-signals"
    sqs_queue: str = "telemetry-fallback"
    mongo_uri: str = "mongodb://mongo:27017/edal"
    incremental_minutes: int = 15
    anomaly_threshold: float = 0.8

    class Config:
        env_file = ".env"

settings = Settings()
