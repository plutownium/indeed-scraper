from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, Text, MetaData, ForeignKey, func
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from bs4 import BeautifulSoup
from langdetect import detect

import sys
sys.path.append("..")

from database.database import SqlPost
from scraper.classes.Query import Query, Page, Post

