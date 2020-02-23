from bs4 import BeautifulSoup
import requests

base_URL = "https://www.indeed.ca"

another_url = "https://www.indeed.ca/jobs?q=developer&l=Vancouver%2C+BC"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
}

r = requests.get(another_url, headers=headers, timeout=5)
soup = BeautifulSoup(r.text, "html.parser")  # https://www.fernandomc.com/posts/using-requests-to-get-and-post/
soup_string = str(soup)

a_tags = soup.find_all("a", {"class": "jobtitle"})

for a in a_tags:
    print(base_URL + a["href"])