from bs4 import BeautifulSoup
import requests
from math import ceil
from .Query import Query










a_query = Query("developer", "Vancouver")
print(a_query.query)
results = a_query
print(results.page_links)
print(results.pages)