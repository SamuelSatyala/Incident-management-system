from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Incident(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))
    description = db.Column(db.Text)

    priority = db.Column(db.String(10))
    status = db.Column(db.String(20), default="Open")

    is_major = db.Column(db.Boolean, default=False)

    # ⭐ NEW FIELDS
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sla_hours = db.Column(db.Integer, default=24)
