# incident-utils-nci

`incident-utils-nci` is the custom object-oriented Python library created for this project. It centralises:

- impact/urgency scoring
- priority calculation
- SLA policy selection
- lightweight dashboard analytics

## Main classes

- `IncidentPriority`: converts impact and urgency into `P1` to `P4`, computes SLA hours, and flags major incidents.
- `SlaClock`: calculates deadline, countdown, and SLA state.
- `IncidentAnalytics`: produces dashboard counters from incident collections.

## Local packaging

Build the library from the project root with:

```bash
python -m build
```

## Publishing

Publish to TestPyPI or PyPI after replacing the placeholder metadata with your own account details:

```bash
python -m twine upload --repository testpypi dist/*
```

Add the published package URL to the project report once uploaded.
