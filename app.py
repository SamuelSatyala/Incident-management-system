import os

from flask import Flask, flash, redirect, render_template, request, url_for
from sqlalchemy import text

from cloud_services import CloudIntegrationManager
from config import Config
from incident_utils import IncidentAnalytics, IncidentPriority, SlaClock
from models import Incident, db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite"):
            with db.engine.connect() as connection:
                connection.execute(text("PRAGMA journal_mode=WAL"))
                connection.execute(text("PRAGMA busy_timeout=30000"))

    cloud_manager = CloudIntegrationManager(app.config)

    @app.context_processor
    def inject_helpers():
        return {
            "cloud_statuses": cloud_manager.describe_services(),
        }

    @app.route("/")
    def index():
        incidents = Incident.query.order_by(Incident.created_at.desc()).all()
        analytics = IncidentAnalytics(incidents)

        return render_template(
            "index.html",
            incidents=incidents,
            analytics=analytics.summary(),
            cloud_summary=cloud_manager.summary(),
            sla_clock=SlaClock,
        )

    @app.route("/incidents", methods=["POST"])
    def create_incident():
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        if not title or not description:
            flash("Title and description are required to create an incident.", "danger")
            return redirect(url_for("index"))

        impact = int(request.form.get("impact", 3))
        urgency = int(request.form.get("urgency", 3))
        priority_engine = IncidentPriority(impact=impact, urgency=urgency)

        incident = Incident(
            title=title,
            description=description,
            service_name="Core Platform",
            reporter_email="system@nci.local",
            impact=impact,
            urgency=urgency,
            priority=priority_engine.calculate_priority(),
            status=request.form.get("status", "Open"),
            is_major=priority_engine.is_major_incident(),
            sla_hours=priority_engine.sla_hours(),
        )

        db.session.add(incident)
        db.session.commit()

        sync_state = safe_record_event(cloud_manager, incident, "incident_created")
        incident.cloud_sync_state = sync_state
        db.session.commit()

        flash(
            f"Incident #{incident.id} created with priority {incident.priority}.",
            "success",
        )
        return redirect(url_for("index"))

    @app.route("/incidents/<int:incident_id>/update", methods=["GET", "POST"])
    def update_incident(incident_id):
        incident = Incident.query.get_or_404(incident_id)

        if request.method == "POST":
            if incident.status == "Closed":
                flash("Closed incidents are locked and cannot be edited.", "danger")
                return redirect(url_for("index"))

            impact = int(request.form.get("impact", 3))
            urgency = int(request.form.get("urgency", 3))
            priority_engine = IncidentPriority(impact=impact, urgency=urgency)

            incident.title = request.form.get("title", incident.title).strip()
            incident.description = request.form.get(
                "description", incident.description
            ).strip()
            incident.impact = impact
            incident.urgency = urgency
            incident.priority = priority_engine.calculate_priority()
            incident.is_major = priority_engine.is_major_incident()
            incident.sla_hours = priority_engine.sla_hours()
            incident.status = request.form["status"]

            if incident.status == "Resolved" and incident.resolved_at is None:
                incident.resolved_at = SlaClock.utcnow()
            elif incident.status != "Resolved":
                incident.resolved_at = None

            db.session.commit()

            sync_state = safe_record_event(cloud_manager, incident, "incident_updated")
            incident.cloud_sync_state = sync_state
            db.session.commit()

            flash(f"Incident #{incident.id} updated.", "success")
            return redirect(url_for("index"))

        return render_template("update.html", incident=incident, sla_clock=SlaClock)

    @app.route("/incidents/<int:incident_id>/delete", methods=["POST"])
    def delete_incident(incident_id):
        incident = Incident.query.get_or_404(incident_id)
        safe_record_event(cloud_manager, incident, "incident_deleted")
        db.session.delete(incident)
        db.session.commit()
        flash(f"Incident #{incident_id} deleted.", "warning")
        return redirect(url_for("index"))

    @app.route("/health")
    def health():
        return {
            "status": "ok",
            "application": "cloud-incident-control-centre",
            "cloud_integrations": cloud_manager.summary(),
        }

    return app


def safe_record_event(cloud_manager, incident, event_name):
    try:
        return cloud_manager.record_event(incident, event_name)
    except Exception as exc:
        print(f"Cloud sync failed for {event_name} on incident {incident.id}: {exc}")
        return "fallback"


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
        use_reloader=False,
    )
