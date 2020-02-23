from scraper.classes.Query import Query
import io

# 2020/02/23 note: This is old code.

# Q: "developer" and "programmer" both return 2100 jobs. are they the same listings?

developer_url = "https://www.indeed.ca/jobs?q=developer&l=Vancouver%2C+BC"
programmer_url = "https://www.indeed.ca/jobs?q=programmer&l=Vancouver%2C+BC"
start_path = "&start="  # To get to page 2, you go, "&start=20". Page 3: "&start=40"

base_amt = 20

job_queries_list = ["Developer", "Programmer", "Software Engineer", "software developer"
                    "junior developer", "jr developer",
                    "web developer"
                    "front end developer", "frontend developer", "backend developer", "back end developer"]

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
}

# What do I want to do?
# I want to get the HTML from each page and store it in a list.
# Maybe a text file so I don't have to repeat the operation. (It'd be faster the 2nd time around to just open the file)
# So go from .get(developer_url) to .get(next_page_url) to .get(next_page_url) until I'm out of pages.
# Store each result in a variable. Let that be the end of step 1.
# END OF STEP 1: "I have a list of HTML from the search results for "developer".
# Repeat for the "programmer" search query. Get them both stored in the program at the same time.

# Now what do I want to do?
# I have the whole search query for "programmer" and "developer" stored in two variables.
# The next step is to pull out the Title, Company, and Summary. Store those in a dictionary.
# The dictionary can look like: {0: [title, company, summary]}

# Ok, what's next?
# For each item in "programmer" and "developer", determine if it is unique or a copy.
# This will take a long time: For each item in "programmer", check if the same item exists in "developer".
# If it does exist in BOTH, add it to a list called "duplicates".
# If it does not exist in both, add it to a list called "uniques".
# Print the length of each list.

# You can make a function called "Compare Queries". Takes two arguments: Query one, query two..
# Returns a dictionary like: {QueryOne: [uniques], QueryTwo: [uniques], duplicates: [dupes]}

# You can make a function called "Tally Results Per Query". Takes one argument, a list of queries.
# Returns a dictionary like: {query1: length_of_results, query2: length_of_results, ... }

# You can make each query into an object. Use OOP!
# Each query can have a


# query = Query(["front end developer", "frontend developer"], "Vancouver")
# print(query.query1)
# print(query.query2)
# q_results = query.compare_queries()
#
# for i in q_results[0]:
#     i.print(company=True)

comparison = Query(["developer", "programmer"], "Vancouver")
print(comparison.query1)
print(comparison.query2)
results = comparison.compare_queries()

# Generate some text files so you don't have to repeat the requests over and over...

with io.open("developer_results.txt", "w", encoding="utf-8") as f:
    f.write("Printed at 8:02 am, February 5th, 2020")

    for a in results[0]:
        posting = "\nTitle: " + str(a.title) + "\nCompany:" + str(a.company) + "\nSummary: " + str(a.summary) + "\n\n*===========*"
        f.write(posting)
f.close()

with io.open("programmer_results.txt", "w", encoding="utf-8") as f:
    f.write("Printed at 8:02 am, February 5th, 2020")

    for b in results[1]:
        posting = "\nTitle: " + str(b.title) + "\nCompany:" + str(b.company) + "\nSummary: " + str(b.summary) + "\n\n*===========*"
        f.write(posting)
f.close()

with io.open("shared_results.txt", "w", encoding="utf-8") as f:
    f.write("Printed at 8:02 am, February 5th, 2020")
    for c in results[2]:
        title = "Title: " + str(c.title) + "\n"
        company = "Company: " + str(c.company) + "\n"
        summary = "Summary: " + str(c.summary) + "\n\n*===========*\n"
        posting = title + company + summary
        f.write(posting)
f.close()

print("Done!")
