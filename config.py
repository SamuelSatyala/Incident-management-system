import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
INSTANCE_DIR.mkdir(exist_ok=True)


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "nci-cloud-project-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(INSTANCE_DIR / 'cloud_incident_control.db').as_posix()}",
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"timeout": 30},
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CLOUD_PROVIDER = os.getenv("CLOUD_PROVIDER", "aws")
    AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")

    S3_ARCHIVE_BUCKET = os.getenv("S3_ARCHIVE_BUCKET", "")
    DYNAMODB_AUDIT_TABLE = os.getenv("DYNAMODB_AUDIT_TABLE", "")
    SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN", "")
    SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL", "")
    CLOUDWATCH_NAMESPACE = os.getenv("CLOUDWATCH_NAMESPACE", "IncidentPlatform")

    ENABLE_CLOUD_FALLBACK = os.getenv("ENABLE_CLOUD_FALLBACK", "true").lower() == "true"
