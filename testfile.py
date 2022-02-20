import os
from sqlalchemy import create_engine, MetaData, Table, insert, String, Column, select, bindparam, or_

#make connection to the database and its information
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))

# Connect to the engine
connection = engine.connect()

# instantiate the MetaData
metadata = MetaData()

# Reflect each table from the database: users, logins, booksearch, searches
users = Table('users', metadata, autoload=True, autoload_with=engine)
logins = Table('logins', metadata, autoload=True, autoload_with=engine)
booksearch = Table('booksearch', metadata, autoload=True, autoload_with=engine)

#print(engine.table_names())

#print(repr(booksearch))

title_search = "Henry James"
stmt = select([booksearch]).where(or_(booksearch.c.author == bindparam('title_search'),
        booksearch.c.title == bindparam('title_search'), booksearch.c.isbn == bindparam('title_search')))
matches = connection.execute(stmt, title_search=title_search).fetchall()
print(matches)
