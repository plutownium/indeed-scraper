import requests
from math import ceil
from time import sleep, time
from bs4 import BeautifulSoup

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from langdetect import detect
from datetime import datetime

# from ...database.database import SqlQuery
# from indeedscraper.database.database import SqlQuery

# ### TEMP:
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

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

    redirect_url = Column(String(1024))
    actual_url = Column(String(1024))
    soup = Column(Text(999999))

    what = Column(String(256))
    where = Column(String(256))
    lang_keywords = Column(String(256))
    pay = Column(String(256))
    title = Column(String(256))
    company = Column(String(256))
    blurb = Column(String(256))
# ### /endTEMP


class Post:
    """A Posting is an object ...
        It has the attributes "job_title", "company", and "blurb", as well as "soup" and "actual_url".
    """

    def __init__(self, redirect, actual=None, soup=None, job_title=None, company=None, blurb=None):
        self.redirect_link = redirect

        self.actual_url = actual
        self.soup = soup

        # Set these after initialization?
        self.title = job_title
        self.company = company
        self.blurb = blurb  # The blurb Indeed chose to use on the Page
        self.salary = ""
        self.ez_apply = None

    # def output(self, show_company=False):
    #     if show_company:
    #         print("\n\nTitle: {}, \nCompany: {}, \nSummary: {}, \nLink: {}\n=========="
    #               .format(self.title, self.company, self.blurb, self.actual_url))
    #     else:
    #         print("\n\nTitle: {}, \nSummary: {}, \nLink: {}\n=========="
    #               .format(self.title, self.blurb, self.actual_url))


class Page:
    """A Page is an object...
        Important to note that self.posts is a list of every Post found on the Page.
    """

    def __init__(self, page_url, soup, page_num=None, num_of_jobs=None, page_links=None):
        self.page_url = page_url
        self.soup = soup

        self.page_num = page_num
        self.num_of_jobs = num_of_jobs
        self.links = page_links

        self.posts = []


class Query:
    """ A Query is an object with arguments query and city.
        A Query contains a collection of Pages(?) which contain Postings
        A Query contains a big list of Postings.
        Can do things like _____ which returns a list of all Pages
        Or _____ which returns a list of all Postings
    """

    base_URL = None

    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                             "(KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"}

    # NOTE: "%2c" is the ascii keycode for comma: https://stackoverflow.com/questions/6182356/what-is-2c-in-a-url
    ca_cities_url_strings = {"Vancouver": "Vancouver%2C+BC",
                             "Toronto": "Toronto%2C+ON",
                             "Ottawa": "Ottawa%2C+ON",
                             "Waterloo": "Waterloo%2C+ON",
                             "Montreal": "Montréal%2C+QC"}
    usa_cities_url_strings = {"Seattle": "Seattle%2C+WA",
                              "New York": "New+York%2C+NY",
                              "Silicon Valley": "Silicon+Valley%2C+CA"}

    def __init__(self, query, city, jobs=None):
        """ Accepts three arguments:
            :query: the search term to query on Indeed [note: .lower()ed for consistency
            :city: either Toronto or Vancouver
            :jobs: used when populating the object for translation into JSON by the REST API
        """
        # ### Start by checking if the query has been done already

        # for use in the "?q=" part of the query
        self.query = query.replace(" ", "+").lower()

        self.city = city
        # for use in the "&l=" part of the query
        if city in self.ca_cities_url_strings.keys():
            self.city_query_string = self.ca_cities_url_strings[city]
            # Edit base_URL based on which country we are in
            self.base_URL = "https://www.indeed.ca"
        elif city in self.usa_cities_url_strings.keys():
            self.city_query_string = self.usa_cities_url_strings[city]
            # Edit base_URL based on which country we are in
            self.base_URL = "https://www.indeed.com"
        else:
            # NOTE: Is this the best way to do this?
            # "Raise an error msg if the supplied city doesn't work for the app"
            # This "else" block should be reached IF AND ONLY IF something fucked up and I don't wanna progress.
            raise ValueError("%s isn't in the list of cities" % city)

        self.URL = self.base_URL + "/jobs?q=" + self.query + "&l=" + self.city_query_string

        # the "jobs" param is supplied while populating the Query object for
        # outbound use in the REST API, and we don't wanna trigger this code block
        # while the Query object is being used for outbound purposes.

        # added note (like a week after adding "if not jobs"):
        # ...uhh... I don't really remember why this is here...
        # The greentext documentation at the top of the __init__ func says:
        # ":jobs: used when populating the object for translation into JSON by the REST API"
        # so I think it's intended to be like: "well, if we see the jobs param passed in (probably as int), then
        # we know the Query object isn't being used to search Indeed; instead it's being used to hold(?) data
        # during the process of extracting data from the db & turning it into JSON to give to the frontend"
        # ... but I could be wrong about that being the intended purpose of this code ...
        # SO UH, in conclusion: "It works, leave it for now."
        if not jobs:
            # ### Get the # of jobs available and divide by 20
            # The original .get request and its soup
            main_page_soup = self.fetch_soup(self.URL)
            # Find the div with id="searchCountPages" and convert it to a string
            total_jobs = str(main_page_soup.find("div", {"id": "searchCountPages"}))
            # Split by " " to extract the # of jobs
            total_jobs = total_jobs.split(" ")
            # Get the jobs value, which is the "len(total_jobs_q) - 2" th entry in the list
            total_jobs = total_jobs[len(total_jobs) - 2]

            # Check if there is a comma present in the string based number
            if "," in total_jobs:
                split = total_jobs.split(",")
                total_jobs = "".join(split)

            # get the # of jobs from the returned array
            self.exact_num_of_jobs = int(total_jobs)

            # divide by 20, use math.ceil() to get # of pages
            self.pages_per_query = int(ceil(self.exact_num_of_jobs / 20))

            print("EXACT # of jobs in query lang: {}, loc: {} is {}".format(query, city, self.exact_num_of_jobs))
            self.done = self.__query_done_already(query, city, self.exact_num_of_jobs)
            if self.done:
                print("Already done the query for {} in {} within the past week".format(query, city))
            else:
                # Get a list of links to each Page in the Query
                self.soups = self.__fetch_all_soup(self.URL, self.pages_per_query)
        else:
            self.jobs_in_query = jobs


    def fetch_soup(self, url):
        page = requests.get(url, headers=self.headers, timeout=5)
        soup = BeautifulSoup(page.text, "html.parser")
        return soup

    def __query_done_already(self, lang, loc, jobs_in_current_search_results):
        """Function checks the current Query object's inputs for similar results in the db and
        returns True if it appears that the search query has already been done.

        Implemented because I was interrupted while running queries on a list of languages & cities and
        I don't want to simply restart from 0. Instead I want to be able to loop over that same list of languages
        & cities each week and have the Query object decide whether to scrape or output objects that trip the following
        function to simply not run.

        Note the db will be queried for results matching lang & loc then we will ask, 'Is there a result with a recent
        timestamp?' and return True if there is one."""

        # MAYBE: If less than 100 jobs in the current search query, just redo the scan.

        engine = create_engine('mysql://root:mysql345@localhost:3306/scrapes?charset=utf8', echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()

        db_has_similar_results = session.query(SqlQuery).filter(SqlQuery.what == lang, SqlQuery.what == loc).all()

        for obj in db_has_similar_results:
            timestamp = obj.created_date
            # "if the timestamp is within a week of today..."
            if check_if_less_than_seven_days(timestamp):
                # Return True if even ONE query was done within the last seven days
                return True
        # Return False if no queries in the search were done within the last seven days
        return False


        # if num_of_jobs_in_db_query > 100:
        #     query_already_run = True
        # else:
        #     # False because it's no trouble to rerun a
        #     query_already_run = False



        # return query_already_run


    def __fetch_all_soup(self, start_url, pages, scrape_individual_posts=False, bother_with_actual_url=False):
        """Takes the Query URL and returns a dictionary of Page objects.
            :start_url: is the url of page 1 in the query, and...
            :pages: is the number of pages in the search query.
        """
        # URL examples:
        # https://www.indeed.ca/jobs?q=javascript+developer&l=Vancouver,+BC&limit=20
        # https://www.indeed.ca/jobs?q=javascript+developer&l=Vancouver,+BC&start=20&limit=20
        # &start=20&limit=20

        pages_as_int = int(pages)

        start = "&start="
        limit = "&limit=20"
        query_soups = {}
        # Steps: Request the page, get the soup, get the Post links, request the Post links,
        # get the Post soup, store the Page and Post soup along with the links.
        print("URL to search: " + str(start_url))

        # blank lines to convince myself that ive successfully updated the bdist file
        #
        #
        #
        #
        #
        # Iterate over every page in the query.
        for i in range(0, pages_as_int):
            # Save the loop's start time
            begin_time = time()

            # Get the Page soup
            url_to_fetch = start_url + start + str(i*20) + limit
            print("Doing .get on {}; loop {} of {}.".format(url_to_fetch, i, pages))
            html = requests.get(url_to_fetch, headers=self.headers, timeout=5)

            # Check status code for 404
            if html.ok:
                # response.ok returns true if status code < 400
                pass
            else:
                # If the response wasn't okay, wait for 20 seconds, then try the request again
                sleep(20)
                html = requests.get(url_to_fetch, headers=self.headers, timeout=5)

            page_soup = BeautifulSoup(html.text, "html.parser")  # I have the Page Soup and Page URL
            # print("PAGE_SOUP LENGTH:" + str(len(page_soup)))

            # ### Get the URL of every Post on the Page (create the Post objects and append them to the Page after)
            post_actual_urls = []
            post_redirect_links = []
            untested_job_cards = page_soup.find_all("div", {"class": "jobsearch-SerpJobCard"})

            job_cards = []
            for card in untested_job_cards:
                card_string = str(card)
                if detect(card_string) == "fr":
                    pass
                else:
                    job_cards.append(card)

            for div in job_cards:
                # Extract the <a> tag...
                just_the_a_tag = div.find("a", {"class": "jobtitle"})
                # ### Get the Actual URL of the Posting...
                redirect_link = self.base_URL + just_the_a_tag["href"]
                post_redirect_links.append(redirect_link)

                # Check if we're scraping the individual Posts, and set bother_w_act_url to true if we are, because
                # we'll need the condition to be true in the next line to trigger the scraping of Actual URLs
                if scrape_individual_posts:
                    bother_with_actual_url = True
                if bother_with_actual_url:
                    actual_url = requests.head(redirect_link, allow_redirects=True).url
                    post_actual_urls.append(actual_url)

            # ### initialize the Page object

            page_object = Page(url_to_fetch, page_soup)

            # print("POST_URLS LENGTH:" + str(len(post_urls)))

            # Decide whether to scrape individual posts, or simply generate Page-based Post objects...
            if scrape_individual_posts:
                for index, actual_url in enumerate(post_actual_urls):
                    html = requests.get(actual_url, headers=self.headers, timeout=5)
                    post_soup = BeautifulSoup(html.text, "html.parser")  # I have the Post soup and the Post URL

                    # ### Create a new Post object, then append the Post object to the Page object
                    new_post_object = Post(post_redirect_links[index], actual=actual_url, soup=post_soup)
                    page_object.posts.append(new_post_object)
            else:  # If not scraping individual posts, forget the soup, just create Post objects with URLs.
                if bother_with_actual_url:
                    for index, actual_url in enumerate(post_actual_urls):
                        new_post_object = Post(post_redirect_links[index], actual_url)
                        page_object.posts.append(new_post_object)
                else:
                    for redir in post_redirect_links:
                        new_post_object = Post(redir)
                        page_object.posts.append(new_post_object)

            # ### Add the Page object with its appended Posts to the Query Soups dictionary
            query_soups[i + 1] = page_object

            seconds = begin_time - time()
            print("Completed loop in {} seconds.".format(seconds))
            # print(query_soups[i+1])
            # print(query_soups[i + 1].posts)

        # End goal: query_soups is a dictionary looking like {1: <Page 1>, 2: <Page 2>, ... }
        # and <Page 1>.posts looks like [<Post1>, <Post2>, ...]

        return query_soups


def check_if_less_than_seven_days(x):
    """Accepts a datetime.datetime object and does heavy math to calculate if 'x - now' is < 7

    Returns True if the input value is from less than 7 days ago."""
    now = datetime.now()
    return (x - now).days < 7

# engine = create_engine('mysql://root:mysql345@localhost:3306/scrapes?charset=utf8', echo=False)
# Session = sessionmaker(bind=engine)
# session = Session()
# db_has_related_results = session.query(SqlQuery).filter(SqlQuery.what == "vue", SqlQuery.where == "Vancouver").first()
# print(db_has_related_results.__dict__)




# TODO: Make Query class run a check to see if a query is already in the db. if in db, skip query -- all within the Query obj, ok?
# TODO: absolve myself of this stupid "ValueError: attempted relative import beyond top-level package" bullshit


