# Architecture Diagram

```mermaid
flowchart LR
    U["Examiner / End User"] --> W["Flask Web App on Public Cloud VM / App Service"]
    W --> DB["Primary Database\nSQLite locally or PostgreSQL on RDS"]
    W --> LIB["Custom Library\nincident-utils-nci"]
    W --> S3["Amazon S3\nArchive snapshots"]
    W --> DDB["Amazon DynamoDB\nAudit records"]
    W --> SNS["Amazon SNS\nMajor incident alerts"]
    W --> SQS["Amazon SQS\nAsync triage queue"]
    W --> CW["Amazon CloudWatch\nCustom metrics"]
    GH["GitHub Actions"] --> W
```

## Architectural patterns used

- Stateless web tier: request handling is separated from durable storage and cloud integrations.
- Managed service integration: core operational concerns are delegated to cloud-native services.
- Queue-based load leveling: SQS supports asynchronous follow-up work.
- Event-driven notification: SNS is triggered on major or resolved incidents.
- Polyglot persistence: relational database for transactional incident data, DynamoDB for audit history, S3 for immutable snapshots.
