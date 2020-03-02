import requests
from math import ceil
from time import sleep, time
from bs4 import BeautifulSoup

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
import sys
sys.path.append(os.path.realpath('...'))
sys.path.insert(0, '')
sys.path.append("...")
sys.path.append("..")

# from ...database.database import SqlQuery
# import

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

    def print(self, show_company=False):
        if show_company:
            print("\n\nTitle: {}, \nCompany: {}, \nSummary: {}, \nLink: {}\n=========="
                  .format(self.title, self.company, self.blurb, self.actual_url))
        else:
            print("\n\nTitle: {}, \nSummary: {}, \nLink: {}\n=========="
                  .format(self.title, self.blurb, self.actual_url))


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
        self.done = self.__query_done_already(query, city)
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
            self.pages_per_query = ceil(self.exact_num_of_jobs / 20)

            # Get a list of links to each Page in the Query
            self.soups = self.__fetch_all_soup(self.URL, self.pages_per_query)
        else:
            self.jobs_in_query = jobs


    def fetch_soup(self, url):
        page = requests.get(url, headers=self.headers, timeout=5)
        soup = BeautifulSoup(page.text, "html.parser")
        return soup

    def __query_done_already(self, lang, loc):
        engine = create_engine('mysql://root:mysql345@localhost:3306/scrapes?charset=utf8', echo=False)
        Session = sessionmaker(bind=engine)
        session = Session()

        db_has_related_results = session.query(SqlQuery).filter(SqlQuery.what == lang, SqlQuery.what == loc)
        print(db_has_related_results)


        return True

    def __fetch_all_soup(self, start_url, pages, scrape_individual_posts=False, bother_with_actual_url=False):
        """Takes the Query URL and returns a dictionary of Page objects.
            :start_url: is the url of page 1 in the query, and...
            :pages: is the number of pages in the search query.
        """
        # URL examples:
        # https://www.indeed.ca/jobs?q=javascript+developer&l=Vancouver,+BC&limit=20
        # https://www.indeed.ca/jobs?q=javascript+developer&l=Vancouver,+BC&start=20&limit=20
        # &start=20&limit=20

        start = "&start="
        limit = "&limit=20"
        query_soups = {}
        # Steps: Request the page, get the soup, get the Post links, request the Post links,
        # get the Post soup, store the Page and Post soup along with the links.
        print("URL to search: " + str(start_url))

        # Iterate over every page in the query.
        for i in range(0, pages):
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
            job_cards = page_soup.find_all("div", {"class": "jobsearch-SerpJobCard"})
            # print("LEN:" + str(len(job_cards)))

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

engine = create_engine('mysql://root:mysql345@localhost:3306/scrapes?charset=utf8', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
db_has_related_results = session.query(SqlQuery).filter(SqlQuery.what == "vue", SqlQuery.what == "Vancouver")
print(db_has_related_results)

# TODO: Make Query class run a check to see if a query is already in the db. if in db, skip query -- all within the Query obj, ok?
# TODO: absolve myself of this stupid "ValueError: attempted relative import beyond top-level package" bullshit

