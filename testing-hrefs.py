import requests
from bs4 import BeautifulSoup
from scraper.scraper import useful_constants

# ### File made to inspect whether I've really successfully gotten the a tag's hrefs or not

BASE_URL = "https://www.indeed.ca"

test_url = "https://www.indeed.ca/jobs?q=programmer&l=Vancouver%2C+BC"
pagination = "&start="

links = []

counter = 0

for page in range(0, 60, 20):
    if page == 0:
        page = requests.get(test_url, timeout=5)
    else:
        # Make the page's soup
        query = test_url + pagination + str(page)
        page = requests.get(query, timeout=5)
    soup = BeautifulSoup(page.text, "html.parser")

    # Find all the useful a tags within the soup
    all_a_tags = soup.find_all("a", {"class": useful_constants.a_href_class})
    print("Collected {} tags!".format(len(all_a_tags)))
    counter += len(all_a_tags)
    for a in all_a_tags:
        link = BASE_URL + a["href"]
        links.append(link)

soups = []  # Will be a list of very long html files
for link in links[:20]:
    # // .head === total magic
    actual_url = requests.head(link, allow_redirects=True).url
    posting = requests.get(actual_url, timeout=5)
    soup = BeautifulSoup(posting.text, "html.parser")
    print(actual_url)
    soups.append(soup)


