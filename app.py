from flask import Flask, session, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ==============================
# Database Connection
# ==============================
def get_db():
    db = sqlite3.connect(os.path.join(BASE_DIR, "blog.db"))
    db.row_factory = sqlite3.Row
    return db

# ==============================
# Create Tables (Auto)
# ==============================
with get_db() as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL,
            image TEXT
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            message TEXT
        )
    """)

# ==============================
# Home Page
# ==============================
@app.route("/")
def home():
    db = get_db()
    articles = db.execute(
        "SELECT * FROM articles ORDER BY id DESC"
    ).fetchall()
    db.close()
    return render_template("index.html", articles=articles)

# ==============================
# Single Article Page
# ==============================
@app.route("/article/<slug>")
def article(slug):
    db = get_db()
    article = db.execute(
        "SELECT * FROM articles WHERE slug=?",
        (slug,)
    ).fetchone()
    db.close()

    if article is None:
        return "Article not found", 404

    return render_template("article.html", article=article)

# ==============================
# About Page
# ==============================
@app.route("/about")
def about():
    return render_template("about.html")

# ==============================
# Admin Dashboard (Add Article)
# ==============================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin"):
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        slug = request.form["slug"]
        content = request.form["content"]
        image = request.form["image"]

        try:
            db = get_db()
            db.execute(
                "INSERT INTO articles (title, slug, content, image) VALUES (?,?,?,?)",
                (title, slug, content, image)
            )
            db.commit()
            db.close()
            return redirect("/admin")

        except sqlite3.IntegrityError:
            return "❌ Slug already exists. Please use a unique slug."

        except Exception as e:
            return f"❌ Error: {e}"

    db = get_db()
    articles = db.execute(
        "SELECT * FROM articles ORDER BY id DESC"
    ).fetchall()
    db.close()

    return render_template("admin.html", articles=articles)

# ==============================
# Login
# ==============================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "owais" and password == "owais123$":
            session["admin"] = True
            return redirect("/admin")

        return "❌ Invalid Credentials"

    return render_template("login.html")

# ==============================
# Logout
# ==============================
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")

# ==============================
# Edit Article
# ==============================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_article(id):
    if not session.get("admin"):
        return redirect("/login")

    db = get_db()

    if request.method == "POST":
        title = request.form["title"]
        slug = request.form["slug"]
        content = request.form["content"]
        image = request.form["image"]

        db.execute("""
            UPDATE articles
            SET title=?, slug=?, content=?, image=?
            WHERE id=?
        """, (title, slug, content, image, id))

        db.commit()
        db.close()
        return redirect("/admin")

    article = db.execute(
        "SELECT * FROM articles WHERE id=?",
        (id,)
    ).fetchone()
    db.close()

    return render_template("edit.html", article=article)

# ==============================
# Delete Article
# ==============================
@app.route("/delete/<int:id>")
def delete_article(id):
    if not session.get("admin"):
        return redirect("/login")

    db = get_db()
    db.execute("DELETE FROM articles WHERE id=?", (id,))
    db.commit()
    db.close()

    return redirect("/admin")

# ==============================
# Contact Page
# ==============================
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        db = get_db()
        db.execute(
            "INSERT INTO messages (name, email, message) VALUES (?,?,?)",
            (name, email, message)
        )
        db.commit()
        db.close()

        return redirect("/contact")

    return render_template("contact.html")

# ==============================
# Run App
# ==============================
if __name__ == "__main__":
    app.run(debug=True)