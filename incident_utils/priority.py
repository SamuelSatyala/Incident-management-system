class IncidentPriority:
    """
    Priority engine for IT Incident Management System

    Uses Impact × Urgency matrix (3-2-1 scale):

        High   = 3
        Medium = 2
        Low    = 1

    Produces priority levels:
        P1 — Critical
        P2 — High
        P3 — Medium
        P4 — Low
    """

    def __init__(self, impact, urgency):
        self.impact = int(impact)
        self.urgency = int(urgency)

    # =========================
    # Calculate Priority
    # =========================
    def calculate_priority(self):

        score = self.impact * self.urgency

        # Realistic ITSM mapping
        if score >= 8:        # 3x3 or 3x2
            return "P1"
        elif score >= 6:      # 3x2 or 2x3
            return "P2"
        elif score >= 3:      # medium combinations
            return "P3"
        else:                 # low combinations
            return "P4"

    # =========================
    # SLA Hours per Priority
    # =========================
    def sla_hours(self):

        priority = self.calculate_priority()

        mapping = {
            "P1": 4,    # Critical — immediate response
            "P2": 8,    # High
            "P3": 24,   # Medium
            "P4": 48    # Low
        }

        return mapping.get(priority, 24)
