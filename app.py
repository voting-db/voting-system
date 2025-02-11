from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///votes.db'
db = SQLAlchemy(app)

# Candidate Model
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    votes = db.Column(db.Integer, default=0)

# Election Settings (Start & End Time)
class ElectionSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

# Create Database
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return redirect(url_for('vote'))

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    candidates = Candidate.query.all()
    settings = ElectionSettings.query.first()
    current_time = datetime.now()

    # Check if voting is allowed
    if settings and (current_time < settings.start_time or current_time > settings.end_time):
        return render_template('vote.html', candidates=None, voting_closed=True)

    if request.method == 'POST':
        candidate_id = request.form.get('candidate')
        if candidate_id:
            selected_candidate = Candidate.query.get(candidate_id)
            if selected_candidate:
                selected_candidate.votes += 1
                db.session.commit()
                return redirect(url_for('results'))
    
    return render_template('vote.html', candidates=candidates, voting_closed=False)

@app.route('/results')
def results():
    candidates = Candidate.query.order_by(Candidate.votes.desc()).all()
    return render_template('results.html', candidates=candidates)

if __name__ == '__main__':
    app.run(debug=True)
