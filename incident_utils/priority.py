class IncidentPriority:
    """
    Reusable priority engine packaged as an installable library component.

    The class converts impact and urgency into both a priority code and
    an SLA policy so the web app and any future workers share the same rules.
    """

    PRIORITY_THRESHOLDS = (
        (8, "P1", 4),
        (6, "P2", 8),
        (3, "P3", 24),
        (0, "P4", 48),
    )

    def __init__(self, impact, urgency):
        self.impact = int(impact)
        self.urgency = int(urgency)

    @property
    def score(self):
        return self.impact * self.urgency

    def calculate_priority(self):
        for threshold, priority, _sla_hours in self.PRIORITY_THRESHOLDS:
            if self.score >= threshold:
                return priority
        return "P4"

    def sla_hours(self):
        for threshold, _priority, sla_hours in self.PRIORITY_THRESHOLDS:
            if self.score >= threshold:
                return sla_hours
        return 48

    def is_major_incident(self):
        return self.calculate_priority() == "P1"

    def as_dict(self):
        return {
            "impact": self.impact,
            "urgency": self.urgency,
            "score": self.score,
            "priority": self.calculate_priority(),
            "sla_hours": self.sla_hours(),
            "is_major": self.is_major_incident(),
        }
