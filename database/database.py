from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Text, ForeignKey, func, DateTime, MetaData
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from bs4 import BeautifulSoup
from langdetect import detect

from datetime import datetime

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
    created_date = Column(DateTime, server_default=func.now())


class SqlPage(Base):
    __tablename__ = "page"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey(SqlQuery.id))
    posts = relationship("SqlPost", backref="page")

    url = Column(String(1024))
    soup = Column(Text(999999))

    what = Column(String(256))
    where = Column(String(256))
    num_of_posts = Column(String(256))


class SqlPost(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    page_parent_id = Column(Integer, ForeignKey(SqlPage.id))
    query_parent_id = Column(Integer, ForeignKey(SqlQuery.id))

    redirect_url = Column(String(2048))
    actual_url = Column(String(2048))
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


def add_plain_query_to_database(query_obj):
    """ Used to unpack the query_obj object and store its data in the database.

    :param query_obj: the result of calling a Query object with what&where params filled in.
    :return: Not a pure function; the whole point of this is to add data to the mySQL db.
    But it DOES :return: False if the passed Query obj was .done and :return: True if the session finished w/o error.
    """
    print("Starting session...")
    if query_obj.done:
        print("Already done...")
        return False
    else:
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
            # query_obj.soups[key].posts is a list of posts (I THINK: note this is a late comment)
            for post in query_obj.soups[key].posts:
                # TODO: Run check "if post is in french, do not add post to db"
                # Note: used to have ".encode("utf-8", errors="ignore")" on the end of post.redirect_link for some reason
                post_to_add = SqlPost(what=query_obj.query,
                                      where=query_obj.city,
                                      redirect_url=post.redirect_link,
                                      actual_url=post.actual_url)
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
        return True


# add_plain_query_to_database(Query("vue", "Vancouver"))

# ### Now pull up: (1) an individual Page and (2) all of its associated Posts, then...
# - get the Title, Company, Salary (if present), and the Blurb, associate them with the Post, and update the Post.

def update_post_from_soup(page_to_edit):
    """ Uses BeautifulSoup to gather data on Posts from a Page Soup.
        Updates the database with complete Posts.
        Does this for an entire Query when you loop thru it properly.

    NOTE: .replace("\u2026", "...") featured everywhere to prevent a bug:
    UnicodeEncodeError: 'ascii' codec can't encode character '\u2026' in position 178: ordinal not in range(128)

    :param page_to_edit: self explanatory. The page that will be selected from the database. An Integer value.
    DEPRECIATED:
    :page_soup: The Page Soup.
    :post_objects: A list of the Page's Post objects from the MySQL database.
    :return: Not a pure function; rather this simply updates the Post in the database.
    """

    my_page_soup = session.query(SqlPage).filter(SqlPage.id == page_to_edit).first().soup
    my_post_objects = session.query(SqlPost).filter(SqlPost.page_parent_id == page_to_edit).all()

    converted_to_soup = BeautifulSoup(my_page_soup, "html.parser")
    job_cards = converted_to_soup.find_all("div", {"class": "jobsearch-SerpJobCard"})

    # Check that things went smoothly; len(job_cards) /should/ equal len(post_objects).

    if len(job_cards) != len(my_post_objects):
        # Note: This error should never happen
        len_job_cards = len(job_cards)
        len_post_objs = len(my_post_objects)
        raise Exception("Something went wrong with lengths: {} for job cards and {} for post objects."
                        .format(len_job_cards, len_post_objs))

    # use Enumerate(list) to give a count which can be used to correlate Card to Post object
    for count, card in enumerate(job_cards):
        # Get the post title
        post_title = card.find_all("a", {"class": "jobtitle"})[0].decode_contents().replace("\u2026", "...")

        # Get the post company
        try:
            # Sometimes the <span> tag has a <a> tag as a child element...
            post_company = card.find("span", {"class": "company"}).find("a").decode_contents().replace("\u2026", "...")
        except AttributeError:
            # ...And sometimes it doesn't.
            try:
                post_company = card.find("span", {"class": "company"}).decode_contents().replace("\u2026", "...")
            except AttributeError:
                post_company = "No company info found"

        # ### Get the post blurb
        try:
            post_blurb_li_tags = card.find("div", {"class": "summary"}).find("ul").find_all("li")
            post_blurb = ""
            for tag in post_blurb_li_tags:
                post_blurb += tag.decode_contents().replace("\u2026", "...")
        except AttributeError:
            post_blurb = str(card.find("div", {"class": "summary"})).replace("\u2026", "...")

        # If the Salary/Pay tag exists, add that too.
        post_pay = card.find("span", {"class": "salaryText"})
        if post_pay:

            post_pay = post_pay.decode_contents().replace("\u2026", "...")
        else:
            post_pay = None

        # ### Correlate Card # to Post Object # and then add the data
        post_to_edit = my_post_objects[count]
        post_to_edit.title = post_title
        post_to_edit.company = post_company
        post_to_edit.blurb = post_blurb
        post_to_edit.pay = post_pay
        session.commit()


def process_entire_query(query_to_process):

    query_language = query_to_process[0]
    query_loc = query_to_process[1]

    # Retrieve the ID of the Query with matching "what" & "where" values
    id_of_query_in_db = session.query(SqlQuery).filter(SqlQuery.what == query_language,
                                                       SqlQuery.where == query_loc).first().id

    query_min_pg = session.query(func.min(SqlPage.id)).filter(SqlPage.parent_id == id_of_query_in_db).scalar()
    query_max_pg = session.query(func.max(SqlPage.id)).filter(SqlPage.parent_id == id_of_query_in_db).scalar()
    for page in range(query_min_pg, query_max_pg + 1):
        update_post_from_soup(page)


def delete_french_posts(lang):
    """ Made this to stop the Vue search query from populating with French language results.
    :param lang: a string. probably "Vue".
    """
    posts = session.query(SqlPost.what == lang).all()
    print(len(posts))
    for post in posts:
        if detect(post.blurb) == "fr":
            session.delete(post)
            session.commit()


def drop_all_tables():
    """Clean the db of all records.

    Quote from S.O.:
    'declarative_base(bind=engine).metadata.drop_all(bind=engine) will drop all tables that it /knows/ about.'
    """
    # (https://stackoverflow.com/questions/50513791/sqlalchemy-metadata-drop-all-does-not-work)
    print("dropping...")
    Base = declarative_base(bind=engine)
    Base.metadata.drop_all()



# # Done
# max_page = session.query(func.max(SqlPage.id)).scalar()
# for i in range(0, max_page):
#     update_post_from_soup(i + 1)


# # ### Example of adding a query to the database and collecting data for Post objects:
# add_plain_query_to_database(Query("PHP", "Vancouver"))
# min_page_php = session.query(func.min(SqlPage.id)).filter(SqlPage.parent_id == 2).scalar()
# max_page_php = session.query(func.max(SqlPage.id)).filter(SqlPage.parent_id == 2).scalar()
# for i in range(min_page_php, max_page_php):
#     update_post_from_soup(i + 1)

# add_plain_query_to_database(Query("angular", "Vancouver"))
# min_page_angular = session.query(func.min(SqlPage.id)).filter(SqlPage.parent_id == 3).scalar()
# max_page_angular = session.query(func.max(SqlPage.id)).filter(SqlPage.parent_id == 3).scalar()
# for i in range(min_page_angular, max_page_angular):
#     update_post_from_soup(i + 1)

# # For some reason this didn't get done
# update_post_from_soup(20)

# Add the query "PHP, Toronto" to the database
# add_plain_query_to_database(Query("php", "Toronto"))
# min_pg_php_toronto = session.query(func.min(SqlPage.id)).filter(SqlPage.parent_id == 4).scalar()
# max_pg_php_toronto = session.query(func.max(SqlPage.id)).filter(SqlPage.parent_id == 4).scalar()
# for i in range(min_pg_php_toronto, max_pg_php_toronto):
#     update_post_from_soup(i)


# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~

# NEW on 2020/02/29: Refreshing ALL data in db and adding a few select cities, languages
# drop_all_tables()


# ### Do a LOT of scraping... Let's see if I get banned... Start time: 6:00 pm
langs_to_add = ["vue", "angular", "react", "html", "css", "javascript", "python", "php", "mongodb", "sql"]
short_langs = ["vue", "angular", "react"]
cities_to_add = ["Vancouver", "Toronto", "Seattle", "New York"]
# ### Add the query "lang, loc" to the database:
for lang in langs_to_add:
    for city in cities_to_add:
        # Add the Query to the db, including its Page Soups and Post objects
        query_status = add_plain_query_to_database(Query(lang, city))
        # Run update_post_from_soup n times for the query
        if query_status:
            process_entire_query([lang, city])


meta = MetaData()
meta.bind = engine
meta.drop_all(engine)

# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~
# *~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~*~





