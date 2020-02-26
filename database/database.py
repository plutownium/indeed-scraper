from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, Text, MetaData, ForeignKey, func
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from bs4 import BeautifulSoup
from langdetect import detect

import sys
sys.path.append("..")

from scraper.classes.Query import Query


# "echo=true" causes the console to display the actual SQL query for table creation
engine = create_engine('mysql://root:mysql345@localhost:3306/scrapes?charset=utf8', echo=False)

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
    blurb = Column(String(256))


Base.metadata.create_all(engine)

# instantiate the session object
Session = sessionmaker(bind=engine)
session = Session()

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


# add_plain_query_to_database(Query("vue", "Vancouver"))

# ### Now pull up: (1) an individual Page and (2) all of its associated Posts, then...
# - get the Title, Company, Salary (if present), and the Blurb, associate them with the Post, and update the Post.


def update_post_from_soup(page_to_edit):
    """ Uses BeautifulSoup to gather data on Posts from a Page Soup.
        Updates the database with complete Posts.

    :param page_to_edit: self explanatory. The page that will be selected from the database. An Integer value.

    DEPRECIATED:
    :param page_soup: The Page Soup.
    :param post_objects: A list of the Page's Post objects from the MySQL database.
    :return: Not a pure function; rather this simply updates the Post in the database.
    """

    my_page_soup = session.query(SqlPage).filter(SqlPage.id == page_to_edit).first().soup
    my_post_objects = session.query(SqlPost).filter(SqlPost.page_parent_id == page_to_edit).all()

    converted_to_soup = BeautifulSoup(my_page_soup, "html.parser")
    job_cards = converted_to_soup.find_all("div", {"class": "jobsearch-SerpJobCard"})

    # Check that things went smoothly; len(job_cards) /should/ equal len(post_objects).

    if len(job_cards) != len(my_post_objects):
        # Note: This error should never happen
        raise Exception("Something went wrong with lengths: {} for job cards and {} for post objects."
                        .format(len(job_cards, len(my_post_objects))))

    # use Enumerate(list) to give a count which can be used to correlate Card to Post object
    for count, card in enumerate(job_cards):
        # Get the post title
        post_title = card.find_all("a", {"class": "jobtitle"})[0].decode_contents()

        # Get the post company
        try:
            # Sometimes the <span> tag has a <a> tag as a child element...
            post_company = card.find("span", {"class": "company"}).find("a").decode_contents()
        except AttributeError:
            # ...And sometimes it doesn't.
            post_company = card.find("span", {"class": "company"}).decode_contents()

        # ### Get the post blurb
        post_blurb_li_tags = card.find("div", {"class": "summary"}).find("ul").find_all("li")
        post_blurb = ""
        for tag in post_blurb_li_tags:
            post_blurb += tag.decode_contents()

        # If the Salary/Pay tag exists, add that too.
        post_pay = card.find("span", {"class": "salaryText"})
        if post_pay:

            post_pay = post_pay.decode_contents()
        else:
            post_pay = None

        # ### Correlate Card # to Post Object # and then add the data
        post_to_edit = my_post_objects[count]
        post_to_edit.title = post_title
        post_to_edit.company = post_company
        post_to_edit.blurb = post_blurb
        post_to_edit.pay = post_pay
        session.commit()

# # Done
# max_page = session.query(func.max(SqlPage.id)).scalar()
# for i in range(0, max_page):
#     update_post_from_soup(i + 1)

# ### Print out all Posts that are likely to be instances of fucking FRENCH


def delete_french_posts(what):
    """ Made this to stop the Vue search query from populating with French language results. """
    posts = session.query(SqlPost.what == what).all()
    print(len(posts))
    for post in posts:
        if detect(post.blurb) == "fr":
            session.delete(post)
            session.commit()




