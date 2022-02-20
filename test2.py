import os
from sqlalchemy import create_engine, MetaData, Table, insert, String, Column, select
from sqlalchemy.orm import scoped_session, sessionmaker

#make connection to the database and its information
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))

db = scoped_session(sessionmaker(bind=engine))


login_username2 = "Alice"

review_book = "Free Will"

review_rating = 4

review_opinion = "Good book."

#user_username = "Bob"
#user_password = "burger"
#db.execute("INSERT INTO users (usernames, passwords) VALUES (:usernames, :passwords)",
            #{"usernames": user_username, "passwords": user_password})
db.execute("INSERT INTO reviews (user, rating, book, opinion) VALUES (:user, :rating, :book, :opinion)",
            {"user": login_username2, "rating": review_rating, "book": review_book, "opinion": review_opinion})
#results = db.execute("SELECT * FROM reviews").fetchall()
#print(results)
db.commit()
db.close()
