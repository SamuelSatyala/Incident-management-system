from datetime import datetime, timedelta


class SlaClock:
    STATUS_WITHIN = "Within SLA"
    STATUS_BREACHED = "Breached"

    @staticmethod
    def utcnow():
        return datetime.utcnow()

    @classmethod
    def deadline(cls, incident):
        return incident.created_at + timedelta(hours=incident.sla_hours)

    @classmethod
    def remaining(cls, incident):
        return cls.deadline(incident) - cls.utcnow()

    @classmethod
    def status(cls, incident):
        if cls.remaining(incident).total_seconds() < 0:
            return cls.STATUS_BREACHED
        return cls.STATUS_WITHIN

    @classmethod
    def countdown(cls, incident):
        remaining = cls.remaining(incident)
        if remaining.total_seconds() <= 0:
            return "BREACHED"

        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        return f"{hours}h {minutes}m"
