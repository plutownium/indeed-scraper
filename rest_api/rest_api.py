from flask import Flask
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import sys
sys.path.append("..")

# print(sys.path)
from database.database import SqlPost
from scraper.classes.Query import Query, Page, Post

# TODO: Retrieve a set of data from the MySQL database
# TODO: Turn that set of data into a JSON object
# TODO: Send that JSON object through a route in Flask
# TODO: Make multiple routes in Flask that correspond to different database requests
# TODO: Have a nice day

app = Flask(__name__)

# Initialize SQLAlchemy engine and start a session
engine = create_engine('mysql://root:mysql345@localhost:3306/scrapes?charset=utf8', echo=False)
Session = sessionmaker(bind=engine)
session = Session()


@app.route("/lang/<language>/loc/<location>", methods=["GET"])
def query(language, location):
    print(language)
    language_list = session.query(SqlPost).filter(SqlPost.what == language, SqlPost.where == location).all()
    json_data = convert_db_query_to_json(language_list)
    # print(session.query(SqlPage))
    return json_data


def convert_db_query_to_json(query_result):
    """ Takes a query into the SqlPost table and turns it into JSON.

    :param query_result: The result of querying the MySQL db Post table for a language & location.
    :return: The query turned into a JSON object that can be sent by the REST API.
    """

    posts = []

    # Make entry 0 in the list (and thus entry 0 in the JSON result) be info about the query, like...
    query_details = {"num_of_posts": len(query_result),
                     "language": query_result[0].what,
                     "location": query_result[0].where }
    posts.append(query_details)

    # Populate a list of Post objects
    for result in query_result:

        new_post = result.__dict__
        del new_post['_sa_instance_state']
        print(new_post)
        posts.append(new_post)

    json_string = json.dumps([post for post in posts])

    return json_string


if __name__ == "__main__":
    app.run()
