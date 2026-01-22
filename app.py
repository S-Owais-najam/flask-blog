from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Database connection
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_db():
    return sqlite3.connect(os.path.join(BASE_DIR, "blog.db"))

# Create table
db = get_db()
db.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        message TEXT
    )
    """)
db.commit()
db.close()

@app.route("/")
def home():
    articles = [
        {
            "title": "Full‑Stack Web Development Roadmap",
            "slug": "fullstack-roadmap",
            "desc": "A complete guide to becoming a professional full‑stack developer.",
            "img": "https://images.unsplash.com/photo-1498050108023-c5249f4df085"
        },
        {
            "title": "Python for Web Developers",
            "slug": "python-web",
            "desc": "Why Python is the top choice for backend development.",
            "img": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f"
        },
        {
            "title": "How Modern Websites Are Built",
            "slug": "modern-websites",
            "desc": "Understanding frontend, backend & deployment.",
            "img": "https://images.unsplash.com/photo-1518770660439-4636190af475"
        }
    ]
    return render_template("index.html", articles=articles)

@app.route("/article/<slug>")
def article(slug):
    return render_template("article.html", slug=slug)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        with get_db() as db:
            db.execute(
                "INSERT INTO messages (name, email, message) VALUES (?,?,?)",
                (name, email, message)
            )
        return redirect("/contact")

    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)
