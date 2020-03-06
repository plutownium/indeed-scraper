from flask import Flask
from flask_cors import CORS
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc

import datetime

import sys
sys.path.append("..")

from database.database import SqlPost, SqlQuery
from scraper.classes.Query import Query, Page, Post

app = Flask(__name__)
CORS(app)

# Initialize SQLAlchemy engine and start a session
engine = create_engine('mysql://root:mysql345@localhost:3306/scrapes?charset=utf8', echo=False)

Session = sessionmaker(bind=engine)
session = Session()

# Check db connection upon startup

session_works = session.query(SqlPost).first()
if session_works:
    pass
else:
    print("Your connection is messed up! But this should never happen")


@app.route("/lang/<language>/loc/<location>", methods=["GET"])
def query(language, location):

    location = location.replace("%20", " ")
    print(language, location)
    Session = sessionmaker(bind=engine)
    current_session = Session()

    one_week_ago = datetime.today() - datetime.timedelta(days=7)

    language_list = current_session.query(SqlPost).filter(SqlPost.what == language,
                                                          SqlPost.where == location,
                                                          SqlPost.created_date >= one_week_ago).all()

    json_data = convert_db_query_to_json(language_list)
    current_session.close()
    # print(session.query(SqlPage))
    return json_data


@app.errorhandler(404)
def page_not_found(error):
    return "404 error message: Invalid URL"


def convert_db_query_to_json(query_result):
    """ Takes a query into the SqlPost table and turns it into JSON.

    :param query_result: The result of querying the MySQL db Post table for a language & location.
    :return: The query turned into a JSON object that can be sent by the REST API.
    """

    print("Query Resutls:", query_result)
    posts = []

    # Make entry 0 in the list (and thus entry 0 in the JSON result) be info about the query, like...
    query_details = {"num_of_posts": len(query_result),
                     "language": query_result[0].what,
                     "location": query_result[0].where}
    posts.append(query_details)

    # Populate a list of Post objects
    for result in query_result:

        new_post = result.__dict__
        del new_post['_sa_instance_state']
        posts.append(new_post)

    json_string = json.dumps([post for post in posts])

    return json_string


# if __name__ == "__main__":
#     app.run(debug=True)

# TODO: git commit -m "added created_date field to SqlPost & SqlPage; updated restAPI to filter recent results."

