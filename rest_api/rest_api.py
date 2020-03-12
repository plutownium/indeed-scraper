from flask import Flask
from flask_cors import CORS, cross_origin
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import datetime

import sys
sys.path.append("..")

from database.database import SqlPost, SqlQuery

app = Flask(__name__)
CORS(app, resources={r'/*': {"origins": "*"}})

# Initialize SQLAlchemy engine and start a session
engine = create_engine('mysql://root:mysql345@localhost:3306/scrapes?charset=utf8', echo=False)

Session = sessionmaker(bind=engine)
session = Session()

# Check db connection upon startup

# Code Disabled because I am no longer
session_works = session.query(SqlQuery).first()
if session_works:
    pass
else:
    print("Your connection is messed up! But this should never happen")


@app.route("/lang/<language>/loc/<location>", methods=["GET"])
@cross_origin()
def query(language, location):

    location = location.replace("%20", " ")
    print(language, location)
    Session = sessionmaker(bind=engine)
    current_session = Session()

    one_week_ago = datetime.datetime.today() - datetime.timedelta(days=7)

    # Note: used to be SqlPost here, where SqlQuery is now
    language_list = current_session.query(SqlQuery).filter(SqlQuery.what == language,
                                                          SqlQuery.where == location,
                                                          SqlQuery.created_date >= one_week_ago).all()

    json_data = convert_db_query_to_json(language_list)
    current_session.close()
    # print(session.query(SqlPage))
    return json_data


@app.errorhandler(404)
def page_not_found(error):
    return "404 error message: Invalid URL"


def convert_db_query_to_json(query_result):
    """ Takes a query into the sqlQuery table and turns it into JSON.

    :param query_result: The result of querying the MySQL db Query table for a language & location.
    :return: The query turned into a JSON object that can be sent by the REST API.
    """

    print("Query Results:", query_result)

    # Do this if query_result is an empty array
    if not query_result:
        query_details = {"num_of_posts": 0,
                         "language": "error",
                         "location": "error",
                         "url": "error"}
        json_string = json.dumps(query_details)
    else:
        query_details = {"num_of_posts": query_result[0].num_of_posts,
                         "language": query_result[0].what,
                         "location": query_result[0].where,
                         "url": query_result[0].url}
        json_string = json.dumps(query_details)

    return json_string


if __name__ == "__main__":
    # app.run(host="165.227.78.120", debug=False)
    app.run(debug=False)
