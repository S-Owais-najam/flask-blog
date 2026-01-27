from flask import Flask, session, render_template, request, redirect, url_for
import pyodbc 
import os
import urllib

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ==============================
# Azure SQL Connection String
# ==============================
raw_connection_string = (
    "Server=tcp:codecrafters.database.windows.net,1433;"
    "Initial Catalog=code_crafter;"
    "Persist Security Info=False;"
    "User ID=Owais;"
    "Password=codecrafter123$;"
    "MultipleActiveResultSets=False;"
    "Encrypt=True;"
    "TrustServerCertificate=False;"
    "Connection Timeout=30;"
)

# Connection string configuration
conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};{raw_connection_string}"

def get_db_conn():
    # Establishes connection to Azure SQL
    return pyodbc.connect(conn_str)

# ==============================
# Database Initialization
# ==============================
def init_db():
    conn = get_db_conn()
    cursor = conn.cursor()
    # Create articles table if not exists
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='articles' AND xtype='U')
        CREATE TABLE articles (
            id INT PRIMARY KEY IDENTITY(1,1),
            title NVARCHAR(255) NOT NULL,
            slug NVARCHAR(255) UNIQUE NOT NULL,
            content NVARCHAR(MAX) NOT NULL,
            image NVARCHAR(MAX)
        )
    """)
    # Create messages table if not exists
    cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='messages' AND xtype='U')
        CREATE TABLE messages (
            id INT PRIMARY KEY IDENTITY(1,1),
            name NVARCHAR(255),
            email NVARCHAR(255),
            message NVARCHAR(MAX)
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ==============================
# Routes
# ==============================

@app.route("/")
def home():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, slug, content, image FROM articles ORDER BY id DESC")
    articles = cursor.fetchall()
    conn.close()
    return render_template("index.html", articles=articles)

@app.route("/article/<slug>")
def article(slug):
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, slug, content, image FROM articles WHERE slug=?", (slug,))
    article_data = cursor.fetchone()
    conn.close()
    if article_data is None:
        return "Article not found", 404
    return render_template("article.html", article=article_data)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin"):
        return redirect("/login")
    conn = get_db_conn()
    cursor = conn.cursor()
    if request.method == "POST":
        title, slug = request.form["title"], request.form["slug"]
        content, image = request.form["content"], request.form["image"]
        try:
            cursor.execute("INSERT INTO articles (title, slug, content, image) VALUES (?,?,?,?)", (title, slug, content, image))
            conn.commit()
            return redirect("/admin")
        except Exception as e:
            return f"❌ Error: {e}"
        finally:
            conn.close()
    cursor.execute("SELECT id, title, slug, content, image FROM articles ORDER BY id DESC")
    articles = cursor.fetchall()
    conn.close()
    return render_template("admin.html", articles=articles)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "owais" and request.form["password"] == "owais123$":
            session["admin"] = True
            return redirect("/admin")
        return "❌ Invalid Credentials"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_article(id):
    if not session.get("admin"):
        return redirect("/login")
    conn = get_db_conn()
    cursor = conn.cursor()
    if request.method == "POST":
        title, slug = request.form["title"], request.form["slug"]
        content, image = request.form["content"], request.form["image"]
        cursor.execute("UPDATE articles SET title=?, slug=?, content=?, image=? WHERE id=?", (title, slug, content, image, id))
        conn.commit()
        conn.close()
        return redirect("/admin")
    cursor.execute("SELECT id, title, slug, content, image FROM articles WHERE id=?", (id,))
    article_data = cursor.fetchone()
    conn.close()
    return render_template("edit.html", article=article_data)

@app.route("/delete/<int:id>")
def delete_article(id):
    if not session.get("admin"):
        return redirect("/login")
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name, email, message = request.form["name"], request.form["email"], request.form["message"]
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (name, email, message) VALUES (?,?,?)", (name, email, message))
        conn.commit()
        conn.close()
        return redirect("/contact")
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)