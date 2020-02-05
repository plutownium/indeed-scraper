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
        self.url = url

    def print(self, show_company=False):
        if show_company:
            print("\n\nTitle: {}, Company: {}, Summary: {}".format(self.title, self.company, self.summary))
        else:
            print("\n\nTitle: {}, Summary: {}".format(self.title, self.summary))


class Page:
    """A Page is an object...
        It has the the attributes "links", "page_num", ... what else?
    """

    def __init__(self, page_num, page_url):
        self.page_num = page_num
        self.page_url = page_url
        self.links = []


class Query:
    """ A Query is an object with attributes query1, query2, city, url1 and url2.
        It has the methods compare_queries and __get_query_tally and __parse.
        A Query contains a collection of Postings.
    """

    def __init__(self, queries, city="Vancouver"):
        """ Accepts two arguments:
            :queries: a list of two search queries, and
            :city: either Toronto or Vancouver
        """
        self.base_URL = "https://www.indeed.ca"
        self.headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                      "(KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
    }
        # make the "?q=" part of the query
        if " " in queries[0]:
            self.query1 = queries[0].replace(" ", "+")
        else:
            self.query1 = queries[0]
        if " " in queries[1]:
            self.query2 = queries[1].replace(" ", "+")
        else:
            self.query2 = queries[1]
        # Make the "&l=" part of the query
        if city == "Vancouver":
            self.city = "Vancouver,+BC"
        elif city == "Toronto":
            self.city = "Toronto,+ON"
        else:
            print("Choose a valid city")
            quit()
        # Set the URLs of query1 and query2
        self.URL = self.base_URL + "/jobs?q=" + self.query1 + "&l=" + self.city
        self.URL2 = self.base_URL + "/jobs?q=" + self.query2 + "&l=" + self.city

        # ### Get the # of jobs available and divide by 20

        # The original 2 .get requests
        base_query1 = requests.get(self.URL, headers=self.headers, timeout=5)
        base_query2 = requests.get(self.URL2, headers=self.headers, timeout=5)

        # Convert to text and parse as html. These results are "page 1"'s two soups & are needed for later
        query1_soup = BeautifulSoup(base_query1.text, "html.parser")
        query2_soup = BeautifulSoup(base_query2.text, "html.parser")

        # Find the div with id="searchCountPages" and convert it to a string
        total_jobs_q1 = str(query1_soup.find("div", {"id": "searchCountPages"}))
        total_jobs_q2 = str(query2_soup.find("div", {"id": "searchCountPages"}))

        # Split by " " to extract the # of jobsy
        total_jobs_q1 = total_jobs_q1.split(" ")
        total_jobs_q2 = total_jobs_q2.split(" ")

        # Get the jobs value, which is the "len(total_jobs_q) - 2" th entry in the list
        total_jobs_q1 = total_jobs_q1[len(total_jobs_q1) - 2]
        total_jobs_q2 = total_jobs_q2[len(total_jobs_q2) - 2]

        # Check if there is a comma present in the string based number
        if "," in total_jobs_q1:
            s_q1 = total_jobs_q1.split(",")
            total_jobs_q1 = "".join(s_q1)
        if "," in total_jobs_q2:
            s_q2 = total_jobs_q2.split(",")
            total_jobs_q2 = "".join(s_q2)

        # get the # of jobs from the returned array
        self.exact_num_of_jobs_q1 = int(total_jobs_q1)
        self.exact_num_of_jobs_q2 = int(total_jobs_q2)

        # divide by 20, use math.ceil() to get # of pages
        self.pages_per_query_q1 = ceil(self.exact_num_of_jobs_q1 / 20)
        self.pages_per_query_q2 = ceil(self.exact_num_of_jobs_q2 / 20)

    def compare_queries(self):
        # ### Now .get request each page and store the resulting list of Posting objects in a variable
        results_q1 = self.__get_query_tally(self.URL, self.pages_per_query_q1, self.exact_num_of_jobs_q1)
        results_q2 = self.__get_query_tally(self.URL2, self.pages_per_query_q2, self.exact_num_of_jobs_q2)

        # ### Parse the results: Meaning, sort into "unique hits A, unique hits B, duplicates".
        result = self.__parse(results_q1, results_q2)

        return result

    def __get_page_job_links(self, url, as_html=False):
        """A method which returns a list of links to job Postings found on a given page.

        :param url: The url from a Page query
        :discontinued param html: The HTML from a Page query (I might try it this way)
        :return: Returns a list of URLs to query for the individual Pages
        """
        # Handle the condition where I want to avoid repeating requests, and just feed in a page's HTML
        # AKA as_html=True
        if as_html:
            a_tags = BeautifulSoup(url.text, "html.parser")
            # Note: Need to doublecheck that I did this right. It could be simply:
            # a_tags = url
        else:
            r = requests.get(url, headers=self.headers, timeout=5)
            soup = BeautifulSoup(r.text, "html.parser")
            soup_string = str(soup)
            a_tags = soup.find_all("a", {"class": "jobtitle"})
        links = []

        for a in a_tags:
            link = self.base_URL + a["href"]
            links.append(link)

        return links

    def __get_query_tally(self, url, pages, expected_tally):
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
            # Pass if the start count is higher than the number of jobs (meaning, if the page has 0 results)
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

        # A simple way of discovering if something unexpected happened.
        if len(posts) == expected_tally:
            print("The rare case where we had exactly the expected number of posts.")
            return posts
        else:
            print("LENGTH of posts:", len(posts))
            return posts

    @staticmethod
    def __parse(results_a, results_b):
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

    @staticmethod
    def __check_for_internal_dupes(posts):
        """Accepts a list of Posting objects and checks them for 'repeat offenders'.
            AKA items in the list more than once.
        """
        duplicate_checker = []
        # Generate a list of every summary in posts while rejecting items already in the list
        for item in posts:
            if item.summary in duplicate_checker:
                print("Duplicate detected")
            else:
                duplicate_checker.append(item.summary)


comparison = Query(["developer", "programmer"], "Vancouver")
print(comparison.query1)
print(comparison.query2)
results = comparison.compare_queries()
print(results)