from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, Text, MetaData, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import sys
sys.path.append("..")

from scraper.classes.Query import Query


# "echo=true" causes the console to display the actual SQL query for table creation
engine = create_engine('mysql://root:mysql345@localhost:3306', echo=False)

# Assign the Database name to Scrapes and create the database if it doesn't exist already
DATABASE = "scrapes"
create_str = "CREATE DATABASE IF NOT EXISTS %s ;" % DATABASE
engine.execute(create_str)

# Tell the engine to use the Scrapes database
use_str = "USE %s" % DATABASE
engine.execute(use_str)


Base = declarative_base()


class SqlQuery(Base):
    __tablename__ = "query"
    id = Column(Integer, primary_key=True)
    pages = relationship("SqlPage", backref="query")
    posts = relationship("SqlPost", backref="query")

    what = Column(String(256))
    where = Column(String(256))
    num_of_pages = Column(Integer)
    num_of_posts = Column(Integer)


class SqlPage(Base):
    __tablename__ = "page"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey(SqlQuery.id))
    posts = relationship("SqlPost", backref="page")

    url = Column(String(512))
    soup = Column(Text(999999))

    what = Column(String(256))
    where = Column(String(256))
    num_of_posts = Column(String(256))


class SqlPost(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    page_parent_id = Column(Integer, ForeignKey(SqlPage.id))
    query_parent_id = Column(Integer, ForeignKey(SqlQuery.id))

    url = Column(String(512))
    soup = Column(Text(999999))

    what = Column(String(256))
    where = Column(String(256))
    lang_keywords = Column(String(256))
    pay = Column(String(256))
    title = Column(String(256))
    company = Column(String(256))


Base.metadata.create_all(engine)

# instantiate the session object
Session = sessionmaker(bind=engine)
session = Session()

# django_query = SqlQuery(what="django", where="Vancouver, BC")
# flask_query = SqlQuery(what="flask", where="Toronto, ON")
# js_dev_query = SqlQuery(what="javascript developer", where="Vancouver, BC")
# print(js_dev_query.id)
#
# session.add(django_query)
# session.add(flask_query)
# session.add(js_dev_query)
#
# # Commit changes into the database
# session.commit()
#
# print(js_dev_query.id)

# ### Generate some data and put it into the database...
# vue_query = Query("vue", "Vancouver")
#
# print("Starting session...")
# session_query = SqlQuery(what=vue_query.query,
#                          where=vue_query.city,
#                          num_of_pages=vue_query.pages_per_query,
#                          num_of_posts=vue_query.exact_num_of_jobs)
# # session.add(session_query)
#
# print(vue_query.soups)
#
# query_to_adds_pages = []
# query_to_adds_posts = []
# for key in vue_query.soups:
#     page_to_add = SqlPage(what=vue_query.query,
#                           where=vue_query.city,
#                           url=vue_query.soups[key].page_url,
#                           soup=vue_query.soups[key].soup.encode("utf-8", errors="ignore"))
#     page_to_adds_posts = []
#     for post in vue_query.soups[key].posts:
#         post_to_add = SqlPost(what=vue_query.query,
#                               where=vue_query.city,
#                               url=post.actual_url.encode("utf-8", errors="ignore"))
#         page_to_adds_posts.append(post_to_add)
#         query_to_adds_posts.append(post_to_add)
#     page_to_add.posts = page_to_adds_posts
#     query_to_adds_pages.append(page_to_add)
#     # session.add(page_to_add)
#
# session_query.pages = query_to_adds_pages
# session_query.posts = query_to_adds_posts
#
# session.add(session_query)
# print("Committing...")
# session.commit()  # should add all the pages and posts to the database


def add_plain_query_to_database(query_obj):
    """ Used to unpack the query_obj object and store its data in the database.

    :param query_obj: the result of calling a Query object with what&where params filled in.
    :return: Not a pure function; the whole point of this is to add data to the mySQL db.
    """
    print("Starting session...")
    session_query = SqlQuery(what=query_obj.query,
                             where=query_obj.city,
                             num_of_pages=query_obj.pages_per_query,
                             num_of_posts=query_obj.exact_num_of_jobs)
    # session.add(session_query)

    query_to_adds_pages = []
    query_to_adds_posts = []
    for key in query_obj.soups:
        page_to_add = SqlPage(what=query_obj.query,
                              where=query_obj.city,
                              url=query_obj.soups[key].page_url,
                              soup=query_obj.soups[key].soup.encode("utf-8", errors="ignore"))
        page_to_adds_posts = []
        for post in query_obj.soups[key].posts:
            post_to_add = SqlPost(what=query_obj.query,
                                  where=query_obj.city,
                                  url=post.actual_url.encode("utf-8", errors="ignore"))
            page_to_adds_posts.append(post_to_add)
            query_to_adds_posts.append(post_to_add)
        page_to_add.posts = page_to_adds_posts
        query_to_adds_pages.append(page_to_add)
        # session.add(page_to_add)

    session_query.pages = query_to_adds_pages
    session_query.posts = query_to_adds_posts

    session.add(session_query)
    print("Committing...")
    session.commit()  # should add all the pages and posts to the database

