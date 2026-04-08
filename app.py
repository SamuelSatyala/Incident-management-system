from flask import Flask, flash, redirect, render_template, request, url_for

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
        impact = int(request.form["impact"])
        urgency = int(request.form["urgency"])
        priority_engine = IncidentPriority(impact=impact, urgency=urgency)

        incident = Incident(
            title=request.form["title"].strip(),
            description=request.form["description"].strip(),
            service_name=request.form["service_name"].strip(),
            reporter_email=request.form["reporter_email"].strip(),
            impact=impact,
            urgency=urgency,
            priority=priority_engine.calculate_priority(),
            status=request.form.get("status", "Open"),
            is_major=priority_engine.is_major_incident(),
            sla_hours=priority_engine.sla_hours(),
        )

        db.session.add(incident)
        db.session.commit()

        sync_state = cloud_manager.record_event(incident, "incident_created")
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

            impact = int(request.form["impact"])
            urgency = int(request.form["urgency"])
            priority_engine = IncidentPriority(impact=impact, urgency=urgency)

            incident.title = request.form["title"].strip()
            incident.description = request.form["description"].strip()
            incident.service_name = request.form["service_name"].strip()
            incident.reporter_email = request.form["reporter_email"].strip()
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

            sync_state = cloud_manager.record_event(incident, "incident_updated")
            incident.cloud_sync_state = sync_state
            db.session.commit()

            flash(f"Incident #{incident.id} updated.", "success")
            return redirect(url_for("index"))

        return render_template("update.html", incident=incident, sla_clock=SlaClock)

    @app.route("/incidents/<int:incident_id>/delete", methods=["POST"])
    def delete_incident(incident_id):
        incident = Incident.query.get_or_404(incident_id)
        cloud_manager.record_event(incident, "incident_deleted")
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


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
