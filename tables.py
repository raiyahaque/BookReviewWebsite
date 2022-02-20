import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(os.getenv("DATABASE_URL"))

#metadata = MetaData()

#connection = engine.connect()

db = scoped_session(sessionmaker(bind=engine))


# Create users table to store usernames and passwords
db.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, usernames VARCHAR UNIQUE, passwords VARCHAR)")

# Store books and their information
db.execute("CREATE TABLE books (id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INTEGER NOT NULL)")

# Reviews table
db.execute("CREATE TABLE reviews (id SERIAL PRIMARY KEY, book_id INTEGER NOT NULL, user_id INTEGER NOT NULL, rating INTEGER NOT NULL, comment VARCHAR NOT NULL, FOREIGN KEY (book_id) REFERENCES books (id), FOREIGN KEY (user_id) REFERENCES users (id))")


#print table Details of users
#print(repr(users))

#insert data into the booksearch table from the csv file
f = open("test.csv") #change to reg csv file
csv_reader = csv.reader(f)

next(csv_reader)
for row in csv_reader:
    #db.execute(insert(booksearch).values(isbn=row[0], title=row[1], author=row[2], year = row[3]))
    db.execute("INSERT INTO books (isbn, title, author, year) VALUES(:isbn, :title, :author, :year)",
            {"isbn": row[0], "title": row[1], "author": row[2], "year": row[3]})
db.commit()
