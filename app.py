from flask import Flask, render_template, request, redirect, url_for, session
import random
import sqlite3
from database import init_db

app = Flask(__name__)
app.secret_key = "supersecretkey"  # required for storing session data

# Initialize database
init_db()

# Function to insert user data
def save_user(name, email, aim, problem, story):
    conn = sqlite3.connect("achiever.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, aim, problem, story) VALUES (?, ?, ?, ?, ?)",
        (name, email, aim, problem, story),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

# Function to save answers
def save_answers(user_id, answers):
    conn = sqlite3.connect("achiever.db")
    cursor = conn.cursor()
    for qid, ans in answers.items():
        cursor.execute(
            "INSERT INTO answers (user_id, question, answer) VALUES (?, ?, ?)",
            (user_id, qid, ans),
        )
    conn.commit()
    conn.close()

# Homepage route
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        aim = request.form["aim"]
        problem = request.form["problem"]
        story = request.form["story"]

        # Save user info in database
        user_id = save_user(name.strip().title(), email.strip(), aim.strip(), problem.strip(), story.strip())
        session["user_id"] = user_id
        session["name"] = name.strip().title()

        return redirect(url_for("questionnaire"))

    return render_template("index.html")

# Questionnaire route
@app.route("/questionnaire", methods=["GET", "POST"])
def questionnaire():
    if "user_id" not in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        answers = request.form.to_dict()
        save_answers(session["user_id"], answers)
        session["answers"] = answers
        return redirect(url_for("results"))

    # AI-style dynamic questions (for now randomised, later real AI)
    questions = [
        {"id": "q1", "text": "When working on your goals, what do you struggle with most?", "options": ["Procrastination", "Discipline", "Clarity", "Consistency"]},
        {"id": "q2", "text": "How do you usually stay motivated?", "options": ["Visualization", "Rewards", "Fear of failure", "I don’t stay motivated"]},
        {"id": "q3", "text": "What describes your current mindset best?", "options": ["Positive", "Negative", "Neutral", "Unstable"]},
        {"id": "q4", "text": "Do you prefer structured routines or flexible schedules?", "options": ["Strict routines", "Flexibility", "Balance of both", "No routine at all"]},
        {"id": "q5", "text": "When facing obstacles, what is your first reaction?", "options": ["Overthinking", "Taking action", "Avoiding", "Seeking help"]},
    ]
    random.shuffle(questions)

    return render_template("questionnaire.html", questions=questions)

# Results route
@app.route("/results")
def results():
    if "name" not in session or "answers" not in session:
        return redirect(url_for("home"))

    return render_template("results.html", name=session["name"], answers=session["answers"])

if __name__ == "__main__":
    app.run(debug=True)
