# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, func, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import time

from scraper.classes.Query import Query


# "echo=true" causes the console to display the actual SQL query for table creation
engine = create_engine('mysql://root:mysql345@localhost:3306/scrapes?charset=utf8', echo=False, encoding="utf-8")

# # Assign the Database name to Scrapes and create the database if it doesn't exist already
# DATABASE = "scrapes"
# create_str = "CREATE DATABASE IF NOT EXISTS %s ;" % DATABASE
# engine.execute(create_str)
#
# # Tell the engine to use the Scrapes database
# use_str = "USE %s" % DATABASE
# engine.execute(use_str)


Base = declarative_base()


class SqlQuery(Base):
    __tablename__ = "query"
    id = Column(Integer, primary_key=True)

    what = Column(String(256))
    where = Column(String(256))
    num_of_pages = Column(Integer)
    num_of_posts = Column(Integer)
    created_date = Column(DateTime, server_default=func.now())

    url = Column(String(256))


Base.metadata.create_all(engine)

# instantiate the session object
Session = sessionmaker(bind=engine)


def add_plain_query_to_database(query_obj):
    """ Used to unpack the query_obj object and store its data in the database.

    :param query_obj: the result of calling a Query object with what&where params filled in.
    :return: Not a pure function; the whole point of this is to add data to the mySQL db.
    But it DOES :return: False if the passed Query obj was .done and :return: True if the session finished w/o error.
    """
    print("Starting session...")
    start_time = time.time()
    if query_obj.done:
        print("Already done...")
        return False
    else:
        session = Session()

        if query_obj.query == "c#":
            lang_var = "csharp"
        elif query_obj.query == "c++":
            lang_var = "cplusplus",
        else:
            lang_var = query_obj.query,

        session_query = SqlQuery(what=lang_var,
                                 where=query_obj.city,
                                 num_of_pages=query_obj.pages_per_query,
                                 num_of_posts=query_obj.exact_num_of_jobs,
                                 url=query_obj.URL)

        session.add(session_query)
        session.commit()
        end_time = time.time()
        print("Committing... Took {} seconds.".format(end_time - start_time))
        # Return True because the process completed without error
        return True


def drop_all_tables():
    """Clean the db of all records.

    Quote from S.O.:
    'declarative_base(bind=engine).metadata.drop_all(bind=engine) will drop all tables that it /knows/ about.'
    """
    # (https://stackoverflow.com/questions/50513791/sqlalchemy-metadata-drop-all-does-not-work)
    print("dropping...")
    Base = declarative_base(bind=engine)
    Base.metadata.drop_all()


# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~

langs_to_add = ["vue", "angular", "react", "html", "css", "javascript", "python", "java",
                "c++", "c#", "c", "ruby", "php", "swift", "mysql", "postgresql", "mongodb", "sql"]

cities_to_add = ["Vancouver", "Toronto", "Seattle", "New York", "Silicon Valley", "Dallas"]
# ### Add the query "lang, loc" to the database:
for lang in langs_to_add:
    for city in cities_to_add:
        add_plain_query_to_database(Query(lang, city))


# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~





