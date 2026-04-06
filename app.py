from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///incidents.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODEL
class Incident(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(200))
    priority = db.Column(db.String(10))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 🔥 SLA BASED ON PRIORITY
def get_sla_hours(priority):
    if priority == "P1":
        return 1
    elif priority == "P2":
        return 2
    elif priority == "P3":
        return 3
    elif priority == "P4":
        return 4
    return 3  # default fallback

def get_sla_status(incident):
    sla_hours = get_sla_hours(incident.priority)
    deadline = incident.created_at + timedelta(hours=sla_hours)

    return "BREACHED" if datetime.utcnow() > deadline else "Within SLA"

def get_countdown(incident):
    sla_hours = get_sla_hours(incident.priority)
    deadline = incident.created_at + timedelta(hours=sla_hours)
    remaining = deadline - datetime.utcnow()

    if remaining.total_seconds() <= 0:
        return "BREACHED"

    hours = int(remaining.total_seconds() // 3600)
    minutes = int((remaining.total_seconds() % 3600) // 60)

    return f"{hours}h {minutes}m"

# HOME
@app.route('/')
def index():
    incidents = Incident.query.all()

    total = len(incidents)
    open_count = len([i for i in incidents if i.status == "Open"])
    major = len([i for i in incidents if i.priority == "P1"])
    breached = len([i for i in incidents if get_sla_status(i) == "BREACHED"])

    return render_template(
        "index.html",
        incidents=incidents,
        total=total,
        open_count=open_count,
        major=major,
        breached=breached,
        get_sla_status=get_sla_status,
        get_countdown=get_countdown
    )

# ADD
@app.route('/add', methods=['POST'])
def add():
    incident = Incident(
        title=request.form['title'],
        description=request.form['description'],
        priority=request.form['priority'],
        status=request.form['status']
    )
    db.session.add(incident)
    db.session.commit()
    return redirect('/')

# UPDATE (LOCK CLOSED)
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    incident = Incident.query.get_or_404(id)

    if request.method == 'POST':

        # 🔒 Prevent editing closed incidents
        if incident.status == "Closed":
            return redirect('/')

        incident.title = request.form['title']
        incident.description = request.form['description']
        incident.priority = request.form['priority']
        incident.status = request.form['status']

        db.session.commit()
        return redirect('/')

    return render_template("update.html", incident=incident)

# DELETE
@app.route('/delete/<int:id>')
def delete(id):
    incident = Incident.query.get_or_404(id)
    db.session.delete(incident)
    db.session.commit()
    return redirect('/')

# RUN
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)