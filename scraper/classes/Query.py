import requests
from math import ceil
from bs4 import BeautifulSoup


class Post:
    """A Posting is an object ...
        It has the attributes "job_title", "company", and "blurb", as well as "soup" and "actual_url".
    """

    def __init__(self, post_url, soup=None, job_title=None, company=None, blurb=None):
        self.actual_url = post_url
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

    base_URL = "https://www.indeed.ca"
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                             "(KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"}

    def __init__(self, query, city="Vancouver"):
        """ Accepts two arguments:
            :queries: a list of two search queries, and
            :city: either Toronto or Vancouver
        """
        # for use in the "?q=" part of the query
        self.query = query.replace(" ", "+")

        # for use in the "&l=" part of the query
        self.city = "Vancouver,+BC" if city == "Vancouver" else "Toronto,+ON"

        # Set the URL of the query
        self.URL = self.base_URL + "/jobs?q=" + self.query + "&l=" + self.city

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

    def fetch_soup(self, url):
        page = requests.get(url, headers=self.headers, timeout=5)
        soup = BeautifulSoup(page.text, "html.parser")
        return soup

    def __fetch_all_soup(self, start_url, pages, scrape_individual_posts=False):
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
            # print("Getting page {} at url {}.".format(i, start_url))
            # Get the Page soup
            url_to_fetch = start_url + start + str(i*20) + limit
            print(url_to_fetch)
            html = requests.get(url_to_fetch, headers=self.headers, timeout=5)
            page_soup = BeautifulSoup(html.text, "html.parser")  # I have the Page Soup and Page URL
            # print("PAGE_SOUP LENGTH:" + str(len(page_soup)))

            # ### Get the URL of every Post on the Page (create the Post objects and append them to the Page after)
            post_urls = []
            job_cards = page_soup.find_all("div", {"class": "jobsearch-SerpJobCard"})
            # print("LEN:" + str(len(job_cards)))

            for div in job_cards:
                # Extract the <a> tag...
                just_the_a_tag = div.find("a", {"class": "jobtitle"})
                # ### Get the Actual URL of the Posting...
                redirect_link = self.base_URL + just_the_a_tag["href"]
                actual_url = requests.head(redirect_link, allow_redirects=True).url

                post_urls.append(actual_url)

            # ### initialize the Page object
            page_object = Page(url_to_fetch, page_soup)

            # print("POST_URLS LENGTH:" + str(len(post_urls)))

            # Decide whether to scrape individual posts, or simply generate Page-based Post objects...
            if scrape_individual_posts:
                for url in post_urls:
                    html = requests.get(url, headers=self.headers, timeout=5)
                    post_soup = BeautifulSoup(html.text, "html.parser")  # I have the Post soup and the Post URL

                    # ### Create a new Post object, then append the Post object to the Page object
                    new_post_object = Post(url, post_soup)
                    page_object.posts.append(new_post_object)
            else:  # If not scraping individual posts, forget the soup, just create Post objects with URLs.
                for url in post_urls:
                    new_post_object = Post(url)
                    page_object.posts.append(new_post_object)

            # ### Add the Page object with its appended Posts to the Query Soups dictionary
            query_soups[i + 1] = page_object
            # print(query_soups[i+1])
            # print(query_soups[i + 1].posts)

        # End goal: query_soups is a dictionary looking like {1: <Page 1>, 2: <Page 2>, ... }
        # and <Page 1>.posts looks like [<Post1>, <Post2>, ...]

        return query_soups

