from bs4 import BeautifulSoup
import requests
from math import ceil


class Posting:
    """A Posting is an object ...
        It has the attributes "job_title", "company", and "summary".
    """

    def __init__(self, job_title, company, summary, url=None):
        self.title = job_title
        self.company = company
        self.summary = summary
        self.actual_url = url

        # Set these after initialization?
        self.salary = ""
        self.ez_apply = None

    def print(self, show_company=False):
        if show_company:
            print("\n\nTitle: {}, \nCompany: {}, \nSummary: {}, \nLink: {}\n=========="
                  .format(self.title, self.company, self.summary, self.actual_url))
        else:
            print("\n\nTitle: {}, \nSummary: {}, \nLink: {}\n=========="
                  .format(self.title, self.summary, self.actual_url))


class Page:
    """A Page is an object...
        It has the the attributes "links", "page_num", ... what else?
    """

    def __init__(self, page_num, page_url, soup):
        self.page_num = page_num
        self.page_url = page_url
        self.soup = soup
        self.links = []  # .append() to self.links after initialization


class Query:
    """ A Query is an object with arguments query and city.
        It has the methods compare_queries and __get_query_tally and __parse.
        A Query contains a collection of Pages(?) which contain Postings
        A Query contains a big list of Postings.
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

    def fetch_soup(self, url):
        page = requests.get(url, headers=self.headers, timeout=5)
        soup = BeautifulSoup(page.text, "html.parser")
        return soup

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

        for link in links:
            page_soup = self.fetch_soup(link)
            page_num = links.index(link)
            page_links = []
            for a_tag in page_soup.find_all("a", {"class": "jobtitle"}):
                redirect_link = a_tag["href"]
                actual_url = requests.head(redirect_link, allow_redirects=True).url
                page_links.append(actual_url)

            # Should result in a Page object where .links is a list of the redirected links to Postings on that page
            page = Page(page_num, link, page_soup, page_links)
            pages.append(page)

        return pages

    # @staticmethod
    # def __check_for_internal_dupes(posts):
    #     """Accepts a list of Posting objects and checks them for 'repeat offenders'.
    #         AKA items in the list more than once.
    #     """
    #     duplicate_checker = []
    #     # Generate a list of every summary in posts while rejecting items already in the list
    #     for item in posts:
    #         if item.summary in duplicate_checker:
    #             print("Duplicate detected")
    #         else:
    #             duplicate_checker.append(item.summary)


class Comparison:
    """Used to compare the contents of two queries.
        Has attributes "query1_uniques", "query2_uniques", "shared_postings"
    """
    # ... maybe ...

    # Waiting to implement methods that analyze the contents of two Query objects in various ways


def compare_queries(main_query, alt):
    # ### Now .get request each page and store the resulting list of Posting objects in a variable
    results_q1 = get_query_tally(main_query.URL, main_query.pages_per_query, main_query.exact_num_of_jobs)
    results_q2 = get_query_tally(alt.URL, alt.pages_per_query, alt.exact_num_of_jobs)

    parsed_result = parse(results_q1, results_q2)

    return parsed_result


# Depreciated (used to be used in "Query" back when it compared two queries)
def get_query_tally(self, url, pages, expected_tally):
    """ Accepts three arguments:
        :url: a query url, something like https://www.indeed.ca/jobs?q=frontend+developer&l=Vancouver%2C+BC
        :pages: how many pages the query has
        :expected_tally: based off of "exact_num_of_jobs_q1/q2", used to verify that every posting was counted
        (NOTE: do something like "if expected_tally = num_of_results, print("good") else print("oh well").)

        Purpose: Store HTML of each query in a list & parse each page into its Title, Company, and Summary.

        Returns a list of Post objects.
    """
    posts = []
    summary_duplicate_checker = []
    title_dupe_checker = []

    # This will take a long time because of all the requests...
    for page in range(0, pages):
        # Pass if the start count is higher than the number of jobs (i.e., if the page would have 0 results)
        if page * 20 > expected_tally:
            pass
        else:
            url_to_get = url + "&filter=0" + "&start=" + str(page * 20)
            # print("Getting URL:", url_to_get)
            # An individual page from the query... looped "pages" amount of times.
            r = requests.get(url_to_get, headers=self.headers, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")

            # ### Get a list of job card divs and separate each one into its Title, Company and Summary
            job_cards = soup.find_all("div", {"class": "jobsearch-SerpJobCard"})

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
                condition1 = summary in summary_duplicate_checker
                condition2 = title in title_dupe_checker
                if condition1 & condition2:
                    # print("Rejecting TITLE: {}\nSUMMARY: {}.\n\n".format(title, summary))
                    pass
                else:
                    # FYI: These two lines MUST go AFTER the "if cond1 & cond2" check seen above. MUST.
                    summary_duplicate_checker.append(summary)
                    title_dupe_checker.append(title)
                    # ### Extract the company...
                    company = div.find("span", {"class": "company"}).text

                    # Create a new Posting object and append it to the list
                    new_job = Posting(title, company, summary)
                    # print(new_job.__dict__["summary"])
                    posts.append(new_job)
    return posts


# Depreciated (used to be used in "Query" back when it compared two queries)
def parse(results_a, results_b):
    """A private method used to create unique_results_q1, unique_results_q2, and shared_results.

    :param results_a: a list of Posting objects
    :param results_b: a list of Posting objects
    :return: [unique_results_q1, unique_results_q2, shared_results]
    """
    unique_results_q1 = []
    unique_results_q2 = []
    shared_results = []
    counter = 0

    # Search for Shared Results by comparing .summary values
    for i in results_a:
        for j in results_b:
            if i.summary == j.summary:
                counter += 1
                print("Shared result: {} equals {}".format(i.title, j.title))
                shared_results.append(i)
    if counter > 0:
        print("Found {} matches!".format(counter))

    # Make a list of the summaries from shared_results
    summaries = [x.summary for x in shared_results]

    # Test whether each item in results a & b are unique items. Add to the unique_results list if it is unique.
    for i in results_a:
        if i.summary not in summaries:
            unique_results_q1.append(i)
    for i in results_b:
        if i.summary not in summaries:
            unique_results_q2.append(i)

    result = [unique_results_q1, unique_results_q2, shared_results]
    return result


comparison = Query("developer", "Vancouver")
print(comparison.query)
results = comparison
print(results)