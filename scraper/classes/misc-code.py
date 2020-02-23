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
