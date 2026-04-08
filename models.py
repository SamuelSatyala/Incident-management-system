from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    service_name = db.Column(db.String(120), nullable=False)
    reporter_email = db.Column(db.String(120), nullable=False)
    impact = db.Column(db.Integer, nullable=False)
    urgency = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.String(10), nullable=False)
    status = db.Column(db.String(20), default="Open", nullable=False)
    is_major = db.Column(db.Boolean, default=False, nullable=False)
    sla_hours = db.Column(db.Integer, default=24, nullable=False)
    cloud_sync_state = db.Column(db.String(50), default="pending", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    resolved_at = db.Column(db.DateTime, nullable=True)

    @property
    def is_breached(self):
        from incident_utils import SlaClock

        return SlaClock.status(self) == SlaClock.STATUS_BREACHED

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "service_name": self.service_name,
            "reporter_email": self.reporter_email,
            "impact": self.impact,
            "urgency": self.urgency,
            "priority": self.priority,
            "status": self.status,
            "is_major": self.is_major,
            "sla_hours": self.sla_hours,
            "cloud_sync_state": self.cloud_sync_state,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }
