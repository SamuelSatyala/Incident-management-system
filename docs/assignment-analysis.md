# Assignment Brief Analysis and Project Mapping

## What the brief requires

1. A complex dynamic cloud-based application deployed on a public cloud platform.
2. Formal functional and non-functional requirements.
3. Critical architecture analysis with a diagram.
4. At least five cloud services used programmatically.
5. At least one new object-oriented library created by the student.
6. Public URL for examiners, without cloud-provider registration.
7. CI/CD and deployment evidence.
8. Submission artefacts including source code, library source, and deployment instructions.

## Gap analysis of the original project

- The original code was mostly a local Flask CRUD app.
- It did not clearly demonstrate five cloud services being used programmatically.
- The custom library existed only as a small helper file, not as a structured package.
- The architecture, requirements, and deployment story were not documented strongly enough for the report.
- The UI and routes were not showing cloud-integration status, which made the cloud dimension hard to demonstrate in class.

## Changes implemented

### 1. Refactored into a cloud-ready incident platform

- Added a proper application factory pattern in `app.py`.
- Added explicit cloud workflow handling through `CloudIntegrationManager`.
- Added a health endpoint for cloud-aware monitoring.

### 2. Upgraded the data model

- Added `service_name`, `reporter_email`, `impact`, `urgency`, `resolved_at`, and `cloud_sync_state`.
- Preserved incident lifecycle features such as edit-locking for closed incidents.

### 3. Added a real custom library

- Turned `incident_utils` into a reusable OO package.
- Added packaging metadata in `pyproject.toml`.
- Added `LIBRARY_README.md` so the library can be built and published separately.

### 4. Added five cloud-service integrations

- Amazon S3 for incident snapshot archival.
- Amazon DynamoDB for append-only audit records.
- Amazon SNS for notification fan-out.
- Amazon SQS for asynchronous incident queueing.
- Amazon CloudWatch for operational metrics.

These integrations support local fallback mode by writing evidence files into `instance/cloud_fallback/` when AWS credentials or resource IDs are not configured. This keeps the app runnable for development while still showing the programmatic integration design clearly in code.

### 5. Improved the demonstration value

- Added cloud status cards to the dashboard.
- Added visible sync state per incident.
- Added richer forms so the priority engine can be demonstrated live using impact and urgency.

## Remaining tasks you must complete outside this sandbox

- Deploy the application to a public cloud URL.
- Configure real AWS resources and environment variables.
- Publish the library and place the final public package URL in the report.
- Replace placeholder personal metadata in `pyproject.toml` with your final details.
