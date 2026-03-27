from flask import Flask, render_template, request, redirect, send_file
import sqlite3
from datetime import datetime
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)

# -------------------------------
# DATABASE CONNECTION
# -------------------------------

def connect_db():
    return sqlite3.connect('library.db')


def init_db():
    conn = connect_db()
    c = conn.cursor()

    # Books table
    c.execute("""
        CREATE TABLE IF NOT EXISTS books(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        author TEXT
        )
    """)

    # Members table
    c.execute("""
        CREATE TABLE IF NOT EXISTS members(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
        )
    """)

    # Issued books table
    c.execute("""
        CREATE TABLE IF NOT EXISTS issues(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER,
        member_id INTEGER,
        issue_date TEXT
        )
    """)

    conn.commit()
    conn.close()


# -------------------------------
# LOGIN
# -------------------------------

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin":
            return redirect('/dashboard')

    return render_template("login.html")


# -------------------------------
# DASHBOARD
# -------------------------------

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


# -------------------------------
# BOOKS
# -------------------------------

@app.route('/books')
def books():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM books")
    books = c.fetchall()
    conn.close()

    return render_template("books.html", books=books)


@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']

    conn = connect_db()
    c = conn.cursor()
    c.execute("INSERT INTO books(title, author) VALUES (?,?)", (title, author))
    conn.commit()
    conn.close()

    return redirect('/books')


# -------------------------------
# MEMBERS
# -------------------------------

@app.route('/members')
def members():
    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM members")
    members = c.fetchall()
    conn.close()

    return render_template("members.html", members=members)


@app.route('/add_member', methods=['POST'])
def add_member():
    name = request.form['name']

    conn = connect_db()
    c = conn.cursor()
    c.execute("INSERT INTO members(name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

    return redirect('/members')


# -------------------------------
# ISSUE BOOK
# -------------------------------

@app.route('/issue', methods=['GET', 'POST'])
def issue():
    conn = connect_db()
    c = conn.cursor()

    if request.method == 'POST':
        book_id = request.form['book_id']
        member_id = request.form['member_id']
        date = datetime.now().strftime("%Y-%m-%d")

        c.execute("INSERT INTO issues(book_id, member_id, issue_date) VALUES (?,?,?)",
                  (book_id, member_id, date))
        conn.commit()

    c.execute("SELECT * FROM books")
    books = c.fetchall()

    c.execute("SELECT * FROM members")
    members = c.fetchall()

    conn.close()

    return render_template("issue_book.html", books=books, members=members)


# -------------------------------
# RETURN BOOK
# -------------------------------

@app.route('/return', methods=['GET', 'POST'])
def return_book():
    conn = connect_db()
    c = conn.cursor()

    if request.method == 'POST':
        book_id = request.form['book_id']
        c.execute("DELETE FROM issues WHERE book_id=?", (book_id,))
        conn.commit()

    conn.close()

    return render_template("return_book.html")


# -------------------------------
# SEARCH BOOK
# -------------------------------

@app.route('/search', methods=['GET', 'POST'])
def search():
    books = []

    if request.method == 'POST':
        keyword = request.form['keyword']

        conn = connect_db()
        c = conn.cursor()
        c.execute("SELECT * FROM books WHERE title LIKE ?", ('%' + keyword + '%',))
        books = c.fetchall()
        conn.close()

    return render_template("search.html", books=books)


# -------------------------------
# REPORTS (PDF)
# -------------------------------

@app.route('/reports')
def reports():
    conn = connect_db()
    c = conn.cursor()

    c.execute("SELECT * FROM books")
    books = c.fetchall()

    c.execute("SELECT * FROM members")
    members = c.fetchall()

    c.execute("SELECT * FROM issues")
    issues = c.fetchall()

    conn.close()

    file_path = "report.pdf"
    pdf = canvas.Canvas(file_path)

    pdf.drawString(200, 800, "Library Report")

    y = 760
    pdf.drawString(50, y, "Books:")
    for b in books:
        y -= 20
        pdf.drawString(60, y, f"{b[1]} by {b[2]}")

    y -= 30
    pdf.drawString(50, y, "Members:")
    for m in members:
        y -= 20
        pdf.drawString(60, y, m[1])

    y -= 30
    pdf.drawString(50, y, "Issued Books:")
    for i in issues:
        y -= 20
        pdf.drawString(60, y, f"Book ID: {i[1]} Member ID: {i[2]}")

    pdf.save()

    return send_file(file_path, as_attachment=True)


# -------------------------------
# RUN APP (IMPORTANT FOR DOCKER)
# -------------------------------

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)