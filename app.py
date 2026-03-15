from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import io

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

app = Flask(__name__)

# -------------------------------
# DATABASE INITIALIZATION
# -------------------------------

def init_db():

    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    # Books table
    c.execute("""
    CREATE TABLE IF NOT EXISTS books(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT
    image TEXT
    )
    """)

    # Issued books table
    c.execute("""
    CREATE TABLE IF NOT EXISTS issues(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    student TEXT
    )
    """)

    # Members table
    c.execute("""
    CREATE TABLE IF NOT EXISTS members(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT
    )
    """)

    conn.commit()
    conn.close()


# -------------------------------
# LOGIN
# -------------------------------

@app.route('/', methods=['GET','POST'])
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

    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM books")
    books = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM issues")
    issues = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM members")
    members = c.fetchone()[0]

    overdue = issues

    conn.close()

    return render_template(
        "dashboard.html",
        books=books,
        issues=issues,
        members=members,
        overdue=overdue
    )


# -------------------------------
# VIEW BOOKS
# -------------------------------

@app.route('/books')
def books():

    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    c.execute("SELECT * FROM books")
    books = c.fetchall()

    conn.close()

    return render_template("books.html", books=books)


# -------------------------------
# DELETE BOOK
# -------------------------------

@app.route('/delete_book/<int:id>')
def delete_book(id):

    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    c.execute("DELETE FROM books WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/books')


# -------------------------------
# EDIT BOOK
# -------------------------------

@app.route('/edit_book/<int:id>', methods=['GET','POST'])
def edit_book(id):

    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    if request.method == 'POST':

        title = request.form['title']
        author = request.form['author']

        c.execute("UPDATE books SET title=?, author=? WHERE id=?",
                  (title, author, id))

        conn.commit()
        conn.close()

        return redirect('/books')

    c.execute("SELECT * FROM books WHERE id=?", (id,))
    book = c.fetchone()

    conn.close()

    return render_template("edit_book.html", book=book)


# -------------------------------
# ADD BOOK
# -------------------------------

@app.route('/add_book', methods=['POST'])
def add_book():

    title = request.form['title']
    author = request.form['author']

    image = request.files['image']
    filename = image.filename

    image.save(os.path.join('static/uploads', filename))

    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    c.execute(
        "INSERT INTO books(title,author,image) VALUES (?,?,?)",
        (title,author,filename)
    )

    conn.commit()
    conn.close()

    return redirect('/books')


# -------------------------------
# ISSUE BOOK
# -------------------------------

@app.route('/issue', methods=['GET','POST'])
def issue():

    if request.method == 'POST':

        book_id = request.form['book_id']
        student = request.form['student']

        conn = sqlite3.connect('library.db')
        c = conn.cursor()

        c.execute("INSERT INTO issues(book_id,student) VALUES (?,?)",(book_id,student))

        conn.commit()
        conn.close()

    return render_template("issue_book.html")


# -------------------------------
# RETURN BOOK
# -------------------------------

@app.route('/return', methods=['GET','POST'])
def return_book():

    if request.method == 'POST':

        book_id = request.form['book_id']

        conn = sqlite3.connect('library.db')
        c = conn.cursor()

        c.execute("DELETE FROM issues WHERE book_id=?",(book_id,))

        conn.commit()
        conn.close()

    return render_template("return_book.html")


# -------------------------------
# MEMBERS
# -------------------------------

@app.route('/members')
def members():

    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    c.execute("SELECT * FROM members")
    members = c.fetchall()

    conn.close()

    return render_template("members.html", members=members)


@app.route('/add_member', methods=['POST'])
def add_member():

    name = request.form['name']
    email = request.form['email']

    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    c.execute("INSERT INTO members(name,email) VALUES (?,?)",
              (name,email))

    conn.commit()
    conn.close()

    return redirect('/members')


# -------------------------------
# SEARCH BOOKS
# -------------------------------

@app.route('/search', methods=['GET','POST'])
def search():

    books = []

    if request.method == 'POST':

        keyword = request.form['keyword']

        conn = sqlite3.connect('library.db')
        c = conn.cursor()

        c.execute("SELECT * FROM books WHERE title LIKE ?",('%'+keyword+'%',))
        books = c.fetchall()

        conn.close()

    return render_template("search.html", books=books)


# -------------------------------
# OVERDUE BOOKS
# -------------------------------

@app.route('/overdue')
def overdue():

    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    c.execute("SELECT * FROM issues")
    issues = c.fetchall()

    conn.close()

    return render_template("overdue.html", issues=issues)


# -------------------------------
# REPORTS
# -------------------------------

@app.route('/reports')
def reports():

    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM books")
    books = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM issues")
    issued = c.fetchone()[0]

    conn.close()

    return render_template("reports.html", books=books, issued=issued)


# -------------------------------
# STATISTICS
# -------------------------------

@app.route('/statistics')
def statistics():

    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM books")
    books = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM issues")
    issues = c.fetchone()[0]

    conn.close()

    return render_template("statistics.html", books=books, issues=issues)


# -------------------------------
# BOOKS PDF REPORT
# -------------------------------

@app.route('/books_report')
def books_report():

    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    c.execute("SELECT * FROM books")
    books = c.fetchall()

    conn.close()

    file = "books_report.pdf"

    pdf = canvas.Canvas(file)

    y = 800

    pdf.drawString(200, 850, "Library Books Report")

    for b in books:
        pdf.drawString(50, y, f"ID: {b[0]}  Title: {b[1]}  Author: {b[2]}")
        y -= 20

    pdf.save()

    return send_file(file, as_attachment=True)


# -------------------------------
# REPORT PAGE
# -------------------------------

@app.route('/reports')
def reports_page():   # rename function
    return render_template("reports.html")


# -------------------------------
# PDF REPORT DOWNLOAD
# -------------------------------

@app.route('/download_report')
def download_report():

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Library Management Report", styles['Title']))
    elements.append(Spacer(1,20))

    conn = sqlite3.connect('library.db')
    c = conn.cursor()

    # SUMMARY
    c.execute("SELECT COUNT(*) FROM books")
    total_books = c.fetchone()[0]

    summary = [
        ["Category","Count"],
        ["Total Books", total_books]
    ]

    table = Table(summary)
    elements.append(table)

    conn.close()

    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="library_report.pdf",
        mimetype='application/pdf'
    )


# -------------------------------
# START APPLICATION
# -------------------------------

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)