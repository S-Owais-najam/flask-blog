from flask import Flask, session, render_template, request, redirect, url_for, jsonify
import pyodbc
import math

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ================= AZURE SQL =================
conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=tcp:codecrafters.database.windows.net,1433;"
    "Database=code_crafter;"
    "Uid=Owais;"
    "Pwd=codecrafter123$;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

def get_db_conn():
    return pyodbc.connect(conn_str)

# ================= UTILS =================
def reading_time(text):
    return math.ceil(len(text.split()) / 200)

# ================= HOME =================
@app.route("/")
def home():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles ORDER BY id DESC")
    articles = cursor.fetchall()
    conn.close()
    return render_template("index.html", articles=articles, reading_time=reading_time)

# ================= ARTICLE =================
@app.route("/article/<slug>")
def article(slug):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles WHERE slug=?", (slug,))
    article = cursor.fetchone()
    conn.close()
    if not article:
        return "Article not found", 404
    return render_template("article.html", article=article, reading_time=reading_time)

# ================= SEARCH =================
@app.route("/search")
def search():
    q = request.args.get("q", "")
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM articles
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY id DESC
    """, (f"%{q}%", f"%{q}%"))
    articles = cursor.fetchall()
    conn.close()
    return render_template("search.html", articles=articles, q=q)

@app.route("/search-suggest")
def search_suggest():
    q = request.args.get("q", "")
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT TOP 5 title FROM articles WHERE title LIKE ?",
        (f"%{q}%",)
    )
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(results)

# ================= ADMIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "owais" and request.form["password"] == "owais123$":
            session["admin"] = True
            return redirect("/admin")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db_conn()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
            INSERT INTO articles (title, slug, content, image)
            VALUES (?,?,?,?)
        """, (
            request.form["title"],
            request.form["slug"],
            request.form["content"],
            request.form["image"]
        ))
        conn.commit()

    cursor.execute("SELECT * FROM articles ORDER BY id DESC")
    articles = cursor.fetchall()
    conn.close()
    return render_template("admin.html", articles=articles)

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db_conn()
    cursor = conn.cursor()

    if request.method == "POST":
        cursor.execute("""
            UPDATE articles
            SET title=?, slug=?, content=?, image=?
            WHERE id=?
        """, (
            request.form["title"],
            request.form["slug"],
            request.form["content"],
            request.form["image"],
            id
        ))
        conn.commit()
        conn.close()
        return redirect("/admin")

    cursor.execute("SELECT * FROM articles WHERE id=?", (id,))
    article = cursor.fetchone()
    conn.close()
    return render_template("edit.html", article=article)

@app.route("/delete/<int:id>")
def delete(id):
    if not session.get("admin"):
        return redirect("/login")
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")

# ================= STATIC PAGES =================
@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (name,email,message)
            VALUES (?,?,?)
        """, (
            request.form["name"],
            request.form["email"],
            request.form["message"]
        ))
        conn.commit()
        conn.close()
        return redirect("/contact")
    return render_template("contact.html")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
