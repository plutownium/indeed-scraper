import requests
from math import ceil
from time import sleep, time
from bs4 import BeautifulSoup

from sqlalchemy import create_engine

from langdetect import detect
from datetime import datetime


from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

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
                              "Silicon Valley": "Silicon+Valley%2C+CA",
                              "Dallas": "Dallas%2C+TX"}

    def __init__(self, query, city):
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

        if query == "c#":
            self.query = "C%23"

        self.URL = self.base_URL + "/jobs?q=" + self.query + "&l=" + self.city_query_string

        # ### Get the # of jobs available and divide by 20
        # The original .get request and its soup
        print("Searching %s" % self.URL)
        main_page_soup = self.fetch_soup(self.URL)
        if self.query == "C%23":
            self.query = "c#"
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


def check_if_less_than_seven_days(x):
    """Accepts a datetime.datetime object and does heavy math to calculate if 'x - now' is < 7

    Returns True if the input value is from less than 7 days ago."""
    now = datetime.now()
    return (x - now).days < 7



