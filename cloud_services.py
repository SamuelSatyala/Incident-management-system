import importlib
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CloudServiceStatus:
    name: str
    purpose: str
    configured: bool
    mode: str


class _LocalFallbackStore:
    def __init__(self, base_path):
        self.base_path = Path(base_path) / "cloud_fallback"
        self.base_path.mkdir(parents=True, exist_ok=True)

    def write(self, service_name, payload):
        file_path = self.base_path / f"{service_name}.jsonl"
        with file_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")


class CloudIntegrationManager:
    def __init__(self, config):
        self.config = config
        self.region = config.get("AWS_REGION", "eu-west-1")
        self.fallback_enabled = config.get("ENABLE_CLOUD_FALLBACK", True)
        self.local_store = _LocalFallbackStore("instance")
        self._boto3 = self._load_boto3()

    @staticmethod
    def _load_boto3():
        try:
            return importlib.import_module("boto3")
        except ModuleNotFoundError:
            return None

    def _client(self, service_name):
        if not self._boto3:
            return None
        return self._boto3.client(service_name, region_name=self.region)

    def _mode(self, configured):
        if configured and self._boto3:
            return "live"
        if self.fallback_enabled:
            return "fallback"
        return "disabled"

    def describe_services(self):
        return [
            CloudServiceStatus(
                name="Amazon S3",
                purpose="Incident evidence archiving",
                configured=bool(self.config.get("S3_ARCHIVE_BUCKET")),
                mode=self._mode(bool(self.config.get("S3_ARCHIVE_BUCKET"))),
            ),
            CloudServiceStatus(
                name="Amazon DynamoDB",
                purpose="Audit trail persistence",
                configured=bool(self.config.get("DYNAMODB_AUDIT_TABLE")),
                mode=self._mode(bool(self.config.get("DYNAMODB_AUDIT_TABLE"))),
            ),
            CloudServiceStatus(
                name="Amazon SNS",
                purpose="Major incident notification fan-out",
                configured=bool(self.config.get("SNS_TOPIC_ARN")),
                mode=self._mode(bool(self.config.get("SNS_TOPIC_ARN"))),
            ),
            CloudServiceStatus(
                name="Amazon SQS",
                purpose="Asynchronous escalation queue",
                configured=bool(self.config.get("SQS_QUEUE_URL")),
                mode=self._mode(bool(self.config.get("SQS_QUEUE_URL"))),
            ),
            CloudServiceStatus(
                name="Amazon CloudWatch",
                purpose="Operational metrics",
                configured=True,
                mode=self._mode(True),
            ),
        ]

    def summary(self):
        services = self.describe_services()
        return {
            "live": sum(1 for service in services if service.mode == "live"),
            "fallback": sum(1 for service in services if service.mode == "fallback"),
            "disabled": sum(1 for service in services if service.mode == "disabled"),
        }

    def record_event(self, incident, event_name):
        payload = {
            "event_name": event_name,
            "incident": incident.to_dict(),
        }

        results = [
            self._archive_to_s3(payload),
            self._write_audit_record(payload),
            self._publish_notification(payload),
            self._queue_follow_up(payload),
            self._publish_metric(payload),
        ]

        return "live" if all(result == "live" for result in results) else "fallback"

    def _archive_to_s3(self, payload):
        bucket = self.config.get("S3_ARCHIVE_BUCKET")
        key = f"incidents/{payload['incident']['id']}/{payload['event_name']}.json"
        if bucket and self._boto3:
            try:
                self._client("s3").put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=json.dumps(payload).encode("utf-8"),
                    ContentType="application/json",
                )
                return "live"
            except Exception as exc:
                self.local_store.write(
                    "s3_archive_error",
                    {"error": str(exc), "bucket": bucket, "key": key, "payload": payload},
                )
        self.local_store.write(
            "s3_archive",
            {"bucket": bucket or "local", "key": key, "payload": payload},
        )
        return "fallback"

    def _write_audit_record(self, payload):
        table = self.config.get("DYNAMODB_AUDIT_TABLE")
        if table and self._boto3:
            try:
                self._client("dynamodb").put_item(
                    TableName=table,
                    Item={
                        "incident_id": {"S": str(payload["incident"]["id"])},
                        "event_name": {"S": payload["event_name"]},
                        "created_at": {
                            "S": payload["incident"]["updated_at"]
                            or payload["incident"]["created_at"]
                        },
                        "priority": {"S": payload["incident"]["priority"]},
                        "status": {"S": payload["incident"]["status"]},
                    },
                )
                return "live"
            except Exception as exc:
                self.local_store.write(
                    "dynamodb_audit_error",
                    {"error": str(exc), "table": table, "payload": payload},
                )
        self.local_store.write("dynamodb_audit", payload)
        return "fallback"

    def _publish_notification(self, payload):
        topic_arn = self.config.get("SNS_TOPIC_ARN")
        should_notify = (
            payload["incident"]["is_major"]
            or payload["incident"]["status"] == "Resolved"
        )
        if not should_notify:
            return "live" if topic_arn and self._boto3 else "fallback"

        message = (
            f"Incident #{payload['incident']['id']} is {payload['incident']['status']} "
            f"with priority {payload['incident']['priority']}."
        )

        if topic_arn and self._boto3:
            try:
                self._client("sns").publish(
                    TopicArn=topic_arn,
                    Subject=f"Incident Event: {payload['event_name']}",
                    Message=message,
                )
                return "live"
            except Exception as exc:
                self.local_store.write(
                    "sns_notifications_error",
                    {"error": str(exc), "topic_arn": topic_arn, "payload": payload},
                )
        self.local_store.write("sns_notifications", {"message": message, "payload": payload})
        return "fallback"

    def _queue_follow_up(self, payload):
        queue_url = self.config.get("SQS_QUEUE_URL")
        if queue_url and self._boto3:
            try:
                self._client("sqs").send_message(
                    QueueUrl=queue_url,
                    MessageBody=json.dumps(payload),
                )
                return "live"
            except Exception as exc:
                self.local_store.write(
                    "sqs_queue_error",
                    {"error": str(exc), "queue_url": queue_url, "payload": payload},
                )
        self.local_store.write("sqs_queue", payload)
        return "fallback"

    def _publish_metric(self, payload):
        namespace = self.config.get("CLOUDWATCH_NAMESPACE", "IncidentPlatform")
        if namespace and self._boto3:
            try:
                self._client("cloudwatch").put_metric_data(
                    Namespace=namespace,
                    MetricData=[
                        {
                            "MetricName": "IncidentEvent",
                            "Value": 1,
                            "Unit": "Count",
                            "Dimensions": [
                                {"Name": "Priority", "Value": payload["incident"]["priority"]},
                                {"Name": "Status", "Value": payload["incident"]["status"]},
                                {"Name": "Event", "Value": payload["event_name"]},
                            ],
                        }
                    ],
                )
                return "live"
            except Exception as exc:
                self.local_store.write(
                    "cloudwatch_metrics_error",
                    {"error": str(exc), "namespace": namespace, "payload": payload},
                )
        self.local_store.write("cloudwatch_metrics", payload)
        return "fallback"
