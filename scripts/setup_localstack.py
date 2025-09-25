import boto3
import os

session = boto3.session.Session()
client_s3 = session.client("s3", endpoint_url="http://localstack:4566")
client_kinesis = session.client("kinesis", endpoint_url="http://localstack:4566")
client_sqs = session.client("sqs", endpoint_url="http://localstack:4566")

bucket = os.getenv("S3_BUCKET", "telemetry-bucket")
stream = os.getenv("KINESIS_STREAM", "telemetry-signals")
queue = os.getenv("SQS_QUEUE", "telemetry-fallback")

def main():
    # Create bucket
    try:
        client_s3.create_bucket(Bucket=bucket)
        print(f"S3 bucket {bucket} created")
    except client_s3.exceptions.BucketAlreadyOwnedByYou:
        print("Bucket already exists")

    # Create kinesis
    try:
        client_kinesis.create_stream(StreamName=stream, ShardCount=1)
        print(f"Kinesis stream {stream} created")
    except client_kinesis.exceptions.ResourceInUseException:
        print("Kinesis stream already exists")

    # Create SQS
    try:
        client_sqs.create_queue(QueueName=queue)
        print(f"SQS queue {queue} created")
    except client_sqs.exceptions.QueueNameExists:
        print("SQS queue already exists")

if __name__ == "__main__":
    main()
