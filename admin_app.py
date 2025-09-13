from flask import Flask, render_template, redirect, url_for
import sqlite3
import os
from fpdf import FPDF

app = Flask(__name__)

# Ensure orders folder exists
if not os.path.exists("orders"):
    os.makedirs("orders")

def get_all_users():
    conn = sqlite3.connect("achiever.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_answers(user_id):
    conn = sqlite3.connect("achiever.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question, answer FROM answers WHERE user_id=?", (user_id,))
    answers = cursor.fetchall()
    conn.close()
    return answers

def generate_journal(user):
    user_id, name, email, aim, problem, story = user

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Create 60 days → 120 pages (Morning/Night)
    for day in range(1, 61):
        # Morning page
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"{name}'s Journal - Day {day} (Morning)", ln=True, align="C")
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"✨ Reflection:\nWhat’s one thing you’re grateful for today?\n\n🌞 Goal Focus:\nWhat’s one step you’ll take today towards {aim}?\n\n💡 Affirmation:\n‘I am capable of overcoming {problem}.’")

        # Night page
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"{name}'s Journal - Day {day} (Night)", ln=True, align="C")
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"🌙 Reflection:\nDid you take your step towards {aim} today?\n\n😌 Relaxation:\nWrite one moment that made you smile.\n\n📖 Lesson:\nWhat did you learn today about overcoming {problem}?")

    # Save PDF
    filename = f"orders/{name}_journal.pdf"
    pdf.output(filename)
    return filename

@app.route("/")
def admin_home():
    users = get_all_users()
    return render_template("admin_home.html", users=users)

@app.route("/generate/<int:user_id>")
def generate(user_id):
    conn = sqlite3.connect("achiever.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        filepath = generate_journal(user)
        return f"✅ Journal created: {filepath}"
    else:
        return "❌ User not found."

if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Runs on different port
