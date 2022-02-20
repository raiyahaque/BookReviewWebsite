import os
import json
import requests

from flask import Flask, session, request, render_template, jsonify, flash, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from testlogin import login_required
from werkzeug.security import check_password_hash, generate_password_hash

#make connection to the database and its information
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))


app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    session.clear()
    return render_template("search.html", message="Search any book using its ISBN number, title, or author.")


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    """Register!"""
    if request.method == 'POST':
        # Get username
        user_username = request.form.get("username")
        # Get password
        user_password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        if confirm_password == user_password and user_username != None and user_password != None:
            if db.execute("SELECT * FROM users WHERE usernames = :user_username", {"user_username": user_username}).rowcount == 0:
                db.execute("INSERT INTO users (usernames, passwords) VALUES (:usernames, :passwords)",
                        {"usernames": user_username, "passwords": generate_password_hash(user_password)})
                db.commit()
                return render_template("login.html", message="Login with username and password.")
            else:
                error = "This username is already taken. Please enter a different username."
                flash(error)
                return redirect("/registration")
        return render_template("login.html", message="Login with username and password!")
    else:
        return render_template("registration.html", message="Register Now!")
        #return render_template("error.html", message="Username already taken.")
    #return render_template("login.html", message="Login with username and password.")

@app.route("/login", methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == "POST":
        login_username = request.form.get("username")
        login_password = request.form.get("password")
        error = None
        #add checking password hash
        table_user = db.execute("SELECT * FROM users WHERE usernames = :login_username", {"login_username": login_username}).fetchone()
        #print(table_user)
        if table_user is None:
            error = "Incorrect username."
        elif not check_password_hash(table_user['passwords'], login_password):
            #print(table_user['passwords'])
            error = "Incorrect password."

        if error is None:
            session.clear()
            session['users.id'] = table_user['id']
            return render_template("search.html", message="Search any book using its ISBN number, title, or author.")

        flash(error)

    return render_template("login.html", message="Login with username and password.")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    user_search = ('%' + request.form.get("Search") + '%').lower()
    #print(user_search)

    results = db.execute("SELECT * FROM books WHERE LOWER(author) LIKE :user_search OR LOWER(title) LIKE :user_search OR isbn LIKE :user_search",
                    {"user_search": user_search}).fetchall()

    #print(results)
    if len(results) == 0:
        error = "No matches found."
        flash(error)
        return render_template("search.html", message="Search any book using its ISBN number, title, or author.")
    else:
        return render_template("matches.html", matches=results)

@app.route("/book/<string:book_title>", methods=['GET', 'POST'])
@login_required
def book_details(book_title):
    if request.method == "POST":
        currentUser = session['users.id']
        review_rating = int(request.form.get("Rating"))
        #print(review_rating)
        review_comment = request.form.get("Review")
        #print(review_opinion)
        row = db.execute("SELECT id FROM books WHERE title = :book_title", {"book_title": book_title}).fetchone()
        title = db.execute("SELECT title FROM books WHERE title = :book_title", {"book_title": book_title}).fetchone()
        #print(title)
        bookId = row[0]
        if db.execute("SELECT * FROM reviews WHERE user_id = :currentUser AND book_id = :bookId", {"currentUser": currentUser, "bookId": bookId}).rowcount == 0:
            db.execute("INSERT INTO reviews (book_id, user_id, rating, comment) VALUES(:book_id, :user_id, :rating, :comment)",
                        {"book_id": bookId, "user_id": currentUser, "rating": review_rating, "comment": review_comment})
            db.commit()
        else:
            flash("You have already submitted a review for this book.")
            return redirect(url_for('book_details', book_title=title[0]))

        return redirect(url_for('book_details', book_title=title[0]))

    else:
        row = db.execute("SELECT id FROM books WHERE title = :book_title", {"book_title": book_title}).fetchone()
        #print(row)
        bookId = row[0]
        booksearches = db.execute("SELECT * FROM books WHERE title = :book_title", {"book_title": book_title}).fetchall()
        book_reviews = db.execute("SELECT usernames, rating, comment FROM users INNER JOIN reviews ON users.id = reviews.user_id WHERE book_id = :bookId", {"bookId": bookId}).fetchall()
        isbn_num = db.execute("SELECT isbn FROM books WHERE title = :book_title", {"book_title": book_title}).fetchone()
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "4H93fcjlbQieCpjM6pOetg", "isbns": isbn_num})
        data = res.json()
        book_ratings_count = data['books'][0]['ratings_count']
        book_avg_rating = data['books'][0]['average_rating']
        return render_template("book.html", booksearches=booksearches, book_reviews=book_reviews, book_avg_rating=book_avg_rating, book_ratings_count=book_ratings_count)

@app.route("/api/<string:isbn>", methods=['GET'])
def api_access(isbn):
    #book_info = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    row = db.execute("SELECT title, author, year, isbn, COUNT(reviews.id) AS review_count, AVG(reviews.rating) AS average_score FROM books INNER JOIN reviews ON books.id = reviews.book_id WHERE books.isbn = :isbn GROUP BY title, author, year, isbn", {"isbn": isbn}).fetchone()
    #print(row)
    if row is None:
        return jsonify({"error": "Invalid isbn."}), 404

    results = dict(row.items())

    results['average_score'] = float("%.2f"%(results['average_score']))
    #print(results)

    return jsonify({
        "title": results['title'],
        "author": results['author'],
        "year": results['year'],
        "isbn": results['isbn'],
        "review_count": results['review_count'],
        "average_score": results['average_score']
        })
