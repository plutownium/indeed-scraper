from bs4 import BeautifulSoup
import requests
from languages_list import languages_list

# started 4:10 pm

# Notes: seems <a> tags often have id="sja0", "sja1", "sja2" etc

# GOAL: search thru every page of the "junior developer" Indeed query and...
# 1) Tally up each time a coding language or technology is mentioned.
# 2) Record a link to each site;
# 3) record data on whether it is EZ-Apply or not;
# 4) record whether I've already applied or not
# 5) Output a list of EZ-Apply search queries and a list of Non-EZ applications

# GOAL: Make the data into a visualization on a website. A pretty website. Greens and yellows.

# Questions: Do "back end developer" and "backend developer" have similar listings?
# How many are the same, how many are unique?
# Question: Does "front end web developer" and "front end developer" have similar listings? How many r same, unique?
# Question: Does "jr" and "junior" developer have similar listings? How many are the same, how many are unique?
# Question: Does "frontend developer" and "front end developer" return similar listings? How many are different?

# URLs have format: "https://www.indeed.ca/jobs?q=" + search query (i.e. junior+developer) +
# "&l=" + location query (i.e. Vancouver,+BC) + "&start=" + query number

Van_URL = "https://www.indeed.ca/jobs?q=junior+developer&l=Vancouver,+BC&start="
another_url = "https://www.indeed.ca/jobs?q=developer&l=Vancouver%2C+BC"
Van_location = "Vancouver,+BC"

job_queries_list = ["Developer", "Programmer", "Software Engineer", "software developer"
                    "junior developer", "jr developer",
                    "web developer"
                    "front end developer", "frontend developer", "backend developer", "back end developer",
                    ]

misc_keywords = [
    "OOP", "Object-Oriented Programming", "Bash", "PowerShell"
]

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
}


r = requests.get(another_url, headers=headers, timeout=5)
soup = BeautifulSoup(r.text, "html.parser")  # https://www.fernandomc.com/posts/using-requests-to-get-and-post/
soup_string = str(soup)

a_tags = soup.find_all("a", {"class": "jobtitle"})

# Get the NAME of the job posting:
for item in a_tags:
    element_as_str = str(item)
    first_index = element_as_str.index("title=")
    # get the index where the URL path starts
    first_index = first_index + len("title=") + 1  # + 1 for the first double-quote
    last_index = element_as_str.index('">')
    name = element_as_str[first_index:last_index]
    print("Name:", element_as_str[first_index:last_index])

print(len(a_tags))

# get all title divs then get the a tag from within each div and get that a tag's href
# combine the href with "www.indeed.ca" and make a request to that page, see what you get
#
# https://linuxhint.com/find_children_nodes_beautiful_soup/
title_divs = soup.find_all("div", {"class": "title"})

job_URLs = []

number_of_job_postings = len(soup.find_all("div", {"class": "jobsearch-SerpJobCard"}))
card_divs = soup.find_all("div", {"class": "jobsearch-SerpJobCard"})
n = 0
# Check if the job posting is an "Easily apply" or not
EZ_apply_jobs = []
for i in card_divs:
    if "Easily apply" in str(i):
        EZ_apply_jobs.append(n)  # Generate a 0-indexed list of which jobs are EZ-apply
    n += 1

# Get the parent element of all the "jobsearch-SerpJobCard" divs
just_results = str(soup.find("td", {"id": "resultsCol"}))

