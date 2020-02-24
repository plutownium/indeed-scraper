from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, Text, MetaData, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# "echo=true" causes the console to display the actual SQL query for table creation
engine = create_engine('mysql://root:mysql345@localhost:3306', echo=True)

# Assign the Database name to Scrapes and create the database if it doesn't exist already
DATABASE = "scrapes"
create_str = "CREATE DATABASE IF NOT EXISTS %s ;" % DATABASE
engine.execute(create_str)

# Tell the engine to use the Scrapes database
use_str = "USE %s" % DATABASE
engine.execute(use_str)

Base = declarative_base()


class Query(Base):
    __tablename__ = "query"
    id = Column(Integer, primary_key=True)
    pages = relationship("Page")
    posts = relationship("Post")

    what = Column(String(32))
    where = Column(String(32))
    num_of_pages = Column(Integer)
    num_of_posts = Column(Integer)


class Page(Base):
    __tablename__ = "page"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey(Query.id))
    posts = relationship("Post")

    url = Column(String(256))
    soup = Column(Text)

    what = Column(String(32))
    where = Column(String(32))
    num_of_posts = Column(String(256))


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    page_parent_id = Column(Integer, ForeignKey(Page.id))
    query_parent_id = Column(Integer, ForeignKey(Query.id))

    url = Column(String(256))
    soup = Column(Text)

    what = Column(String(256))
    where = Column(String(256))
    lang_keywords = Column(String(256))
    pay = Column(String(256))
    title = Column(String(256))
    company = Column(String(256))


# instantiate the session object
Session = sessionmaker(bind=engine)
session = Session()

django_query = Query(what="django", where="Vancouver, BC")
flask_query = Query(what="flask", where="Toronto, ON")
js_dev_query = Query(what="javascript developer", where="Vancouver, BC")
print(js_dev_query.id)

session.add(django_query)
session.add(flask_query)
session.add(js_dev_query)

# Commit changes into the database
session.commit()

print(js_dev_query.id)
