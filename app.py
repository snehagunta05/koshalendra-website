import os
import re
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, abort

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-before-going-live")
ADMIN_KEY = os.environ.get("ADMIN_KEY", "change-me")
DB = os.path.join(os.path.dirname(__file__), "academy.db")

# ---- Edit your content here ----
ACADEMY = {
    "name": "Koshalendra Skill Academy",
    "tagline": "Learn Skills • Build Projects • Get Placed",
    "phones": ["9110527593", "6304713524"],
    "email": "contact@koshalendrafoundation.org",
    "website": "www.koshalendrafoundation.org",
    "location": "Hyderabad, Telangana",
    "batch_text": "New batch launching 21st September 2026",
}

COURSES = {
    "Cybersecurity": [
        "Offensive Security (OffSec)",
        "Defensive Security (DefSec)",
        "Cyber Crime Investigation & Digital Forensics (CCIDF)",
        "Governance, Risk & Compliance (GRC)",
        "Ethical Hacking & Cybersecurity Fundamentals",
    ],
    "Emerging Technologies": [
        "Artificial Intelligence & ML", "Data Science", "Blockchain", "AR/VR",
        "Robotics & Automation", "Drone Technology",
        "Embedded Systems & IoT", "PCB Design & Fabrication",
    ],
    "Software & Management": [
        "Java Full Stack Development", "Python Full Stack Development",
        "Product Management",
    ],
}

FEATURES = [
    ("Practical Learning", "Learn by doing, not just by reading."),
    ("Industry Focused", "Courses designed as per real-world requirements."),
    ("Expert Trainers", "Learn from experienced professionals."),
    ("Career Support", "Resume, interview and placement help (where available)."),
]

MODES = [
    ("Offline", "Classroom programmes in Hyderabad with lab sessions."),
    ("Online", "Live instructor-led classes for remote learners."),
    ("Hybrid", "A mix of online and offline learning."),
]

WHO_CAN_JOIN = [
    "Intermediate students", "ITI students", "Diploma students",
    "Undergraduate students", "Graduates", "Job seekers",
    "Working professionals", "Career switchers", "Entrepreneurs",
    "Technology enthusiasts",
]

WHY = [
    "Quality training with expert faculty",
    "Modern labs and real-time projects",
    "Affordable and flexible learning options",
    "Industry-relevant curriculum",
    "Strong career support",
]


# ---- Database ----
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS enquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                course TEXT NOT NULL,
                mode TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )""")


# ---- Routes ----
@app.route("/")
def home():
    return render_template("index.html", a=ACADEMY, courses=COURSES,
                           features=FEATURES, modes=MODES,
                           who=WHO_CAN_JOIN, why=WHY)


@app.route("/enquire", methods=["POST"])
def enquire():
    f = request.form
    name = f.get("name", "").strip()
    phone = re.sub(r"\D", "", f.get("phone", ""))[-10:]
    course = f.get("course", "").strip()

    if not name or len(phone) != 10 or not course:
        flash("Please enter your name, a valid 10-digit phone number and a course.", "error")
        return redirect(url_for("home") + "#enroll")

    with get_db() as db:
        db.execute(
            "INSERT INTO enquiries (name, phone, email, course, mode, message) VALUES (?,?,?,?,?,?)",
            (name, phone, f.get("email", "").strip(), course,
             f.get("mode", ""), f.get("message", "").strip()),
        )
    flash("Thank you! Our team will call you soon.", "success")
    return redirect(url_for("home") + "#enroll")


@app.route("/admin")
def admin():
    if request.args.get("key") != ADMIN_KEY:
        abort(404)
    with get_db() as db:
        rows = db.execute("SELECT * FROM enquiries ORDER BY id DESC").fetchall()
    return render_template("admin.html", rows=rows, a=ACADEMY)


init_db()

if __name__ == "__main__":
    app.run(debug=True)
