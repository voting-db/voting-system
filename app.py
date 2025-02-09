from flask import Flask, render_template, request, session
import sqlite3
import os
import datetime

app = Flask(__name__)

# Secure Secret Key for Sessions
app.secret_key = os.getenv("SECRET_KEY", "SuperSecretKey123")  

# Voting deadline (Change if needed)
VOTING_DEADLINE = datetime.datetime(2025, 2, 15, 18, 0, 0)

# Initialize Database
def init_db():
    conn = sqlite3.connect("voting.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id TEXT UNIQUE,
            voter_name TEXT,
            voter_ip TEXT UNIQUE,
            candidate TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

# Home Route
@app.route("/")
def home():
    if datetime.datetime.now() > VOTING_DEADLINE:
        return "Voting has ended!"
    return render_template("vote.html")

# Handle Voting
@app.route("/vote", methods=["POST"])
def vote():
    if datetime.datetime.now() > VOTING_DEADLINE:
        return "Voting has ended!"
    
    voter_id = request.form.get("voter_id")
    voter_name = request.form.get("voter_name")
    candidate = request.form.get("candidate")
    voter_ip = request.remote_addr  

    if not voter_id or not candidate or not voter_name:
        return "Invalid vote submission!"
    
    conn = sqlite3.connect("voting.db")
    c = conn.cursor()
    
    try:
        c.execute("INSERT INTO votes (voter_id, voter_name, voter_ip, candidate) VALUES (?, ?, ?, ?)",
                  (voter_id, voter_name, voter_ip, candidate))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        return "You have already voted!"
    
    conn.close()
    return "Thank you for voting!"

# Secure Results Page (Admin Only)
@app.route("/results")
def results():
    admin_pass = request.args.get("password")
    if admin_pass != os.getenv("ADMIN_PASSWORD", "Admin123"):  
        return "Unauthorized Access!"
    
    conn = sqlite3.connect("voting.db")
    c = conn.cursor()
    c.execute("SELECT candidate, COUNT(*) FROM votes GROUP BY candidate")
    results = c.fetchall()
    conn.close()
    return render_template("results.html", results=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
