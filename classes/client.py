import requests
from bs4 import BeautifulSoup
from math import ceil
from scraper.scraper import useful_constants
from timeit import default_timer as timer

# TODO: Make this object store its resulting data in a database.
# TODO: Use the data from the database in Query.py, Page.py, and Posting.py


class Client:
    """Retrieves the Soups for all Pages and Postings within a Query"""

    base_URL = "https://www.indeed.ca"
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                             "(KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"}

    def __init__(self, query, city):
        # for use in the "?q=" part of the query
        self.query = query.replace(" ", "+")

        # for use in the "&l=" part of the query
        self.city = "Vancouver,+BC" if city == "Vancouver" else "Toronto,+ON"

        # Set the URL of the query
        self.URL = self.base_URL + "/jobs?q=" + self.query + "&l=" + self.city

        main_page_soup = self.__fetch_soup(self.URL)
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

        self.query_soups = self.__fetch_all_soups(self.URL, self.pages_per_query, self.exact_num_of_jobs)

    def __fetch_soup(self, url):
        page = requests.get(url, headers=self.headers, timeout=5)
        soup = BeautifulSoup(page.text, "html.parser")
        return soup

    def __fetch_all_soups(self, url, pages, jobs):
        """

        :param url: the base query url, which is self.URL
        :param pages: the number of pages in the Query
        :param jobs:  the number of jobs listed in the Query
        :return: a list of links to each individual page in the Query

        Also tracks the amount of TIME spent doing this...
        """

        # ### Get all links to individual pages
        page_links = []
        for page in range(0, pages):
            if page * 20 > jobs:
                print("There's no results at URL: {}".format(url + "&filter=0" + "&start=" + str(page * 20)))
                pass
            else:
                page_url = url + "&filter=0" + "&start=" + str(page * 20)
                page_links.append(page_url)

        # ### Get links to each page's individual postings and build a dictionary
        speed_counter = 0
        start_time = timer()

        # generate a key for the dict
        key = 0
        soups = {}
        for page in page_links:
            # The list where the page's actual_urls will be stored
            page_posting_links = []
            response = requests.get(page, headers=self.headers, timeout=5)
            if response.status_code != 200:
                print("boo! Response status code is {}".format(response.status_code))

            # Get the HTML from the response
            the_pages_soup = BeautifulSoup(response.text, "html.parser")
            # Find all a tags with the useful class attached
            posting_hrefs = the_pages_soup.find_all("a", {"class": useful_constants.a_href_class})
            # Iterate thru the useful a tags, follow the redirect, append the actual link to the Posting
            for link in posting_hrefs:
                redirect_link = self.base_URL + link["href"]
                # Get the URL of the head (whatever that is)
                actual_link = requests.head(redirect_link, allow_redirects=True).url  # How long does this take?
                page_posting_links.append(actual_link)

            # ### Get the soups of each individual posting on the page
            page_postings_soups = []
            for posting in page_posting_links:
                response = requests.get(posting, headers=self.headers, timeout=5)
                if response.status_code != 200:
                    print("boo! Response status code is {}".format(response.status_code))
                # prints the allotted time of operation
                speed_counter += timer() - start_time
                print("Total time elapsed: ", speed_counter)
                # Get the HTML from the response
                the_postings_soup = BeautifulSoup(response.text, "html.parser")
                page_postings_soups.append(the_postings_soup)
            soups[key] = [the_pages_soup, page_posting_links, page_postings_soups]

        end_time = timer()
        print("That took {} seconds.".format(end_time - start_time))

        return soups

# .query_soups[i] contains a page's soup,
# the posting links found on that page (a list),
# and the soups of those postings (also a list)


a = Client("frontend developer", "Vancouver")
print("TEST:", a.query, a.city, a.URL, a.exact_num_of_jobs, a.pages_per_query)
print(a.query_soups[0][1])
