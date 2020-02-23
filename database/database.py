from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, Text, MetaData


# "echo=true" causes the console to display the actual SQL query for table creation
engine = create_engine('mysql://root:mysql345@localhost:3306', echo=True)

# Assign the Database name to Scrapes and create the database if it doesn't exist already
DATABASE = "scrapes"
create_str = "CREATE DATABASE IF NOT EXISTS %s ;" % DATABASE
engine.execute(create_str)

# Tell the engine to use the Scrapes database
use_str = "USE %s" % DATABASE
engine.execute(use_str)

meta = MetaData()

query = Table(
    'query', meta,
    Column('id', Integer, primary_key=True),
    Column('what', String(256)),
    Column('where', String(256)),
    Column("num_of_pages", Integer),
    Column("num_of_posts", Integer)
    # Column("page_soups", String), # Store Soups in the Page table because otherwise the data is too long
    

    # What else do I want to have in my Query Table?
)

page = Table(
    "page", meta,
    Column('id', Integer, primary_key=True),
    Column('what', String(256)),
    Column('where', String(256)),
    Column("page_url", String(256)),
    Column("num_of_posts", String(256)),
    Column("soup", Text)
)

posting = Table(
    "posting", meta,
    Column('id', Integer, primary_key=True),
    Column('what', String(256)),
    Column('where', String(256)),
    Column("lang_keywords", String(256)),
    Column("pay", String(256)),
    Column("title", String(256)),
    Column("company", String(256)),
    Column("soup", Text)
)

# Check if the tables exist before creating them
query_table_exists = engine.dialect.has_table(engine, "query")
page_table_exists = engine.dialect.has_table(engine, "page")
posting_table_exists = engine.dialect.has_table(engine, "posting")
if not query_table_exists:
    if not page_table_exists:
        if not posting_table_exists:
            meta.create_all(engine)

