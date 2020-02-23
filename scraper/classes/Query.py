import requests
from math import ceil
from bs4 import BeautifulSoup
from .Page import Page
from .Posting import Posting


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
        self.soups = self.__fetch_all_soup()

    def fetch_soup(self, url):
        page = requests.get(url, headers=self.headers, timeout=5)
        soup = BeautifulSoup(page.text, "html.parser")
        return soup

    # def __fetch_all_soup(self, url, ):
    #     """Takes the Query URL and returns a list of soups.
    #         Index 0 in the list is a list of all Pages soups.
    #         Indexes 1 to N are Postings soups.
    #     """
    #
    #     page_soups = []
    #     query_soups = []
    #
    #     return query_soups

    @staticmethod
    def __get_links_to_query_pages(url, pages, jobs):
        """From the base query url, returns a list of links to each individual Page in the Query.
        Expects values like...
        url: "https://www.indeed.ca/jobs?q=front+end+developer&l=Vancouver%2C+BC",
        pages: ceil(302 / 20) = 16
        jobs: 302
        :param url: the base query url, which is self.URL
        :param pages: the number of pages in the Query
        :param jobs:  the number of jobs listed in the Query
        :return: a list of links to each individual page in the Query
        """
        page_links = []
        for page in range(0, pages):
            if page * 20 > jobs:
                print("There's no results at URL: {}".format(url + "&filter=0" + "&start=" + str(page * 20)))
                pass
            else:
                page_url = url + "&filter=0" + "&start=" + str(page * 20)
                page_links.append(page_url)

        return page_links


# Notes:
    # Get a list of Page objects, where Pages have .soup
    # From each Page.soup, get the Postings from that Page, incl. the actual_urls
    # What do I want?
    # For Queries to have a list of Pages and a list of Postings.
    # Each Page will have a .page_num, a .page_url, a .soup, a .links list,
    # Each Posting will have a .title, .company, a .summary and a .actual_url

    def __get_page_postings(self, page_url):
        """A method which returns a list Posting objects found on a given Page.
            (The list of links is then used to generate Postings...?)
        :param page_url: The url from a Page query
        :return: Returns a list of Posting objects.
        """

        posts = []
        summary_dupe_checker = []
        title_dupe_checker = []

        page_soup = self.fetch_soup(page_url)
        job_cards = page_soup.find_all("div", {"class": "jobsearch-SerpJobCard"})
        # a_tags = page_soup.find_all("a", {"class": "jobtitle"})

        for div in job_cards:
            # ### Extract the summary...
            try:
                summary = div.find("div", {"class": "summary"}).find("ul").find("li")
            # This Except block handles one unique case which has no inner <ul> or <li> tags
            except AttributeError as ex:
                print("ERROR:", ex)
                print("Couldn't .find() on: ", div.find("div", {"class": "summary"}))
                summary = div.find("div", {"class": "summary"})

            # ### Extract the title...
            just_the_a_tag = div.find("a", {"class": "jobtitle"})
            a_tag_as_string = str(just_the_a_tag)
            first_index = a_tag_as_string.index("title=")
            # + 1 to get to the first double-quote
            first_index = first_index + len("title=") + 1
            # Find where the title ends, right next to the tag close
            last_index = a_tag_as_string.index('">')
            title = str(a_tag_as_string[first_index:last_index])

            # ### Check if "summary" is in the list of summaries already seen. (Check for duplicates.)
            condition1 = summary in summary_dupe_checker
            condition2 = title in title_dupe_checker
            if condition1 & condition2:
                # print("Rejecting TITLE: {}\nSUMMARY: {}.\n\n".format(title, summary))
                pass
            else:
                # FYI: These two lines MUST go AFTER the "if cond1 & cond2" check seen above. MUST.
                summary_dupe_checker.append(summary)
                title_dupe_checker.append(title)
                # ### Extract the company...
                company = div.find("span", {"class": "company"}).text

                # ### Get the Actual URL of the Posting...
                redirect_link = self.base_URL + just_the_a_tag["href"]
                actual_url = requests.head(redirect_link, allow_redirects=True).url

                # Create a new Posting object and append it to the list
                new_job = Posting(title, company, summary, actual_url)
                # print(new_job.__dict__["summary"])
                posts.append(new_job)

        return posts

    def __get_page_list(self, links):
        """A method which returns a list of Page objects with their data filled in.

        :param links: A list of every link to a Page from a given query.
        :return: A list of Page objects with their data filled in.
        """

        pages = []

        for link_to_page in links:
            page_soup = self.fetch_soup(link_to_page)
            page_num = links.index(link_to_page)
            page_links = []
            for a_tag in page_soup.find_all("a", {"class": "jobtitle"}):
                redirect_link = self.base_URL + a_tag["href"]
                actual_url = requests.head(redirect_link, allow_redirects=True).url
                page_links.append(actual_url)

            # Should result in a Page object where .links is a list of the redirected links to Postings on that page

            page = Page(page_num, link_to_page, page_soup, page_links)
            pages.append(page)

        return pages