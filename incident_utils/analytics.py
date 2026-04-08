class IncidentAnalytics:
    def __init__(self, incidents):
        self.incidents = list(incidents)

    def summary(self):
        breached = sum(1 for incident in self.incidents if incident.is_breached)

        return {
            "total": len(self.incidents),
            "open": sum(1 for incident in self.incidents if incident.status == "Open"),
            "resolved": sum(
                1 for incident in self.incidents if incident.status == "Resolved"
            ),
            "major": sum(1 for incident in self.incidents if incident.is_major),
            "breached": breached,
        }
