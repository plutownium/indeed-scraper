import sys
sys.path.append("..")

from ..scraper.classes.Query import Query
from .database import add_plain_query_to_database, process_entire_query

langs_to_add = ["vue", "angular", "react", "html", "css", "javascript", "python", "php", "mongodb", "sql"]
short_langs = ["vue", "angular", "react"]
cities_to_add = ["Vancouver", "Toronto", "Seattle", "New York"]
# ### Add the query "lang, loc" to the database:
for lang in langs_to_add:
    for city in cities_to_add:
        # Add the Query to the db, including its Page Soups and Post objects
        query_status = add_plain_query_to_database(Query(lang, city))
        # Run update_post_from_soup n times for the query
        if query_status:
            process_entire_query([lang, city])


# Note: Run this file to update the scrape data in your DB.


