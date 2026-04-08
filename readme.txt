Cloud Incident Control Centre
=============================

1. Project purpose
This project is a cloud-oriented IT incident management system created for the NCI Cloud Platform Programming assignment. It supports incident creation, SLA tracking, major incident detection, and cloud workflow logging.

2. Main technologies
- Python 3.11+
- Flask
- Flask-SQLAlchemy
- Optional boto3 for live AWS integrations

3. Custom library
The reusable object-oriented library is the `incident_utils` package. Packaging metadata is in `pyproject.toml`.

4. Cloud services integrated programmatically
- Amazon S3
- Amazon DynamoDB
- Amazon SNS
- Amazon SQS
- Amazon CloudWatch

5. Local setup
- Create a virtual environment
- Install dependencies from `requirements.txt`
- Set environment variables as needed
- Run `python app.py`

6. Key environment variables
- `SECRET_KEY`
- `DATABASE_URL`
- `AWS_REGION`
- `S3_ARCHIVE_BUCKET`
- `DYNAMODB_AUDIT_TABLE`
- `SNS_TOPIC_ARN`
- `SQS_QUEUE_URL`
- `CLOUDWATCH_NAMESPACE`
- `ENABLE_CLOUD_FALLBACK`

7. Deployment notes
- For production, use PostgreSQL or Amazon RDS instead of SQLite.
- Deploy to a public cloud service such as AWS EC2, AWS Elastic Beanstalk, or Azure App Service.
- Configure the environment variables on the cloud host.
- Ensure the deployed application is publicly reachable by URL and does not require examiner login.

8. CI/CD
The repository already includes a GitHub Actions deployment workflow in `.github/workflows/deploy.yml`. Update the workflow to match the final hosting environment and secrets.

9. Submission artefacts
- Application source code is in the project root.
- Library source code is in `incident_utils/`.
- Report support documents are in `docs/`.

10. Important finalisation tasks
- Publish the custom library and add the package URL to the report.
- Deploy the app to a public cloud URL and include that URL in the report.
- Remove the bundled `venv/` from the final source ZIP if your lecturer expects a clean source-only submission.
