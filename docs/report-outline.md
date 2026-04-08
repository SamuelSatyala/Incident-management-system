# Report Outline Support

## Suggested application title

Cloud Incident Control Centre: A Cloud-Native Incident Management and SLA Monitoring Platform

## Suggested abstract points

- Web application for logging, updating, and resolving IT incidents.
- Uses a custom object-oriented library to calculate priority and SLA policy.
- Integrates five AWS services for archive, audit, queueing, notifications, and metrics.
- Supports CI/CD through GitHub Actions and can be deployed publicly for examiner access.
- Demonstrates cloud design patterns including managed services, queue-based decoupling, and event-driven notifications.

## Functional requirements

- Create incidents with title, service, reporter, description, impact, and urgency.
- Automatically calculate priority and SLA targets.
- Update incidents and lock closed incidents.
- View dashboard counters for open, resolved, major, and breached incidents.
- Record workflow events to cloud services.
- Provide a public web URL and health endpoint.

## Non-functional requirements

- Public accessibility without examiner registration.
- Availability through cloud deployment.
- Scalability through managed services and asynchronous processing.
- Maintainability through service-layer separation and reusable library design.
- Auditability through immutable snapshot and audit logging.
- Portability through environment-variable configuration and local fallback mode.

## Cloud-service justification starter

- Amazon S3: cheap, durable storage for evidence-style JSON snapshots.
- Amazon DynamoDB: low-latency append-only audit log without schema migration overhead.
- Amazon SNS: simple pub/sub fan-out for notifications to email or other subscribers.
- Amazon SQS: decouples incident ingestion from downstream triage workers.
- Amazon CloudWatch: native metrics and alarms for operational monitoring.
- RDS or managed PostgreSQL: suitable production upgrade from SQLite for transactional incident data.

## Reflection prompts

- What changed when moving from a local CRUD system to a cloud-oriented architecture?
- Which cloud services were easiest and hardest to integrate?
- How did fallback mode help local development and testing?
- What trade-offs appeared between simplicity, cost, and cloud realism?
