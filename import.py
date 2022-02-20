import os
from sqlalchemy import create_engine, MetaData, Table, String, Column, insert, Integer
import csv


engine = create_engine(os.getenv("DATABASE_URL"))

connection = engine.connect()
metadata = MetaData()

booksearch = Table('booksearch', metadata,
            Column('isbn', String(255)),
            Column('title', String(255)),
            Column('author', String(255)),
            Column('year', Integer))
metadata.create_all(engine)


f = open("test.csv") #change to reg csv file
reader = csv.reader(f)

next(reader)
for row in reader:
    connection.execute(insert(booksearch).values(isbn=row[0], title=row[1], author=row[2], year = row[3]))
