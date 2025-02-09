from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import datetime

app = Flask(__name__)
app.secret_key = "secret_key_here"

# Voting deadline (Set your desired date & time)
VOTING_DEADLINE = datetime.datetime(2025, 2, 15, 18, 0, 0)

# Database Setup (Using SQLite)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///voting.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database Model
class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.String(100), unique=True, nullable=False)  # Unique voter ID
    voter_ip = db.Column(db.String(100), unique=True, nullable=False)  # Unique IP
    candidate = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Home Route (Voting Page)
@app.route("/")
def home():
    if datetime.datetime.now() > VOTING_DEADLINE:
        return "Voting has ended!"
    return render_template("vote.html")

# Handle Vote Submission
@app.route("/vote", methods=["POST"])
def vote():
    if datetime.datetime.now() > VOTING_DEADLINE:
        return "Voting has ended!"
    
    voter_id = request.form.get("voter_id")  # Unique voter ID (user input)
    voter_ip = request.remote_addr  # Get voter IP
    candidate = request.form.get("candidate")  # Use .get() to avoid KeyError
    
    if not candidate or not voter_id:
        return "Invalid vote submission!"
    
    existing_vote = Vote.query.filter((Vote.voter_id == voter_id) | (Vote.voter_ip == voter_ip)).first()
    if existing_vote:
        return "You have already voted!"
    
    new_vote = Vote(voter_id=voter_id, voter_ip=voter_ip, candidate=candidate)
    db.session.add(new_vote)
    db.session.commit()
    
    return "Thank you for voting!"

# Show Results
@app.route("/results")
def results():
    votes = db.session.query(Vote.candidate, db.func.count(Vote.id)).group_by(Vote.candidate).all()
    return render_template("results.html", results=votes)

if __name__ == "__main__":
    app.run(debug=True)
