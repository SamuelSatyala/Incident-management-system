from flask import Flask, render_template, request, redirect
from models import db, Incident
from incident_utils.priority import IncidentPriority
from config import Config
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


# =========================
# Priority Escalation
# =========================
def escalate_priority(priority):

    mapping = {
        "P4": "P3",
        "P3": "P2",
        "P2": "P1",
        "P1": "P1"
    }

    return mapping.get(priority, priority)


# =========================
# SLA Breach Check
# =========================
def is_breached(incident):

    deadline = incident.created_at + timedelta(hours=incident.sla_hours)

    return datetime.utcnow() > deadline


# =========================
# DASHBOARD
# =========================
@app.route("/")
def index():

    incidents = Incident.query.all()

    breached_count = sum(1 for i in incidents if is_breached(i))

    return render_template(
        "index.html",
        incidents=incidents,
        is_breached=is_breached,
        breached_count=breached_count
    )


# =========================
# CREATE INCIDENT
# =========================
@app.route("/create", methods=["GET", "POST"])
def create():

    if request.method == "POST":

        title = request.form.get("title")
        description = request.form.get("description")
        impact = request.form.get("impact")
        urgency = request.form.get("urgency")

        # Extra protection: ignore empty submissions
        if not title:
            return redirect("/create")

        engine = IncidentPriority(impact, urgency)

        priority = engine.calculate_priority()
        sla_hours = engine.sla_hours()

        is_major = True if priority == "P1" else False

        incident = Incident(
            title=title,
            description=description,
            priority=priority,
            sla_hours=sla_hours,
            is_major=is_major
        )

        db.session.add(incident)
        db.session.commit()

        # Redirect prevents resubmission on refresh
        return redirect("/")

    return render_template("create.html")


# =========================
# UPDATE INCIDENT
# =========================
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):

    incident = Incident.query.get_or_404(id)

    if request.method == "POST":

        incident.title = request.form.get("title")
        incident.description = request.form.get("description")
        incident.status = request.form.get("status")

        if incident.status == "Open" and incident.priority != "P1":
            incident.priority = escalate_priority(incident.priority)

        incident.is_major = True if incident.priority == "P1" else False

        db.session.commit()

        return redirect("/")

    return render_template("update.html", incident=incident)


# =========================
# DELETE INCIDENT
# =========================
@app.route("/delete/<int:id>")
def delete(id):

    incident = Incident.query.get_or_404(id)

    db.session.delete(incident)
    db.session.commit()

    return redirect("/")


# =========================
# RUN APP — FIXED
# =========================
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)