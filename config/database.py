from pymongo import MongoClient, DESCENDING, ASCENDING
from dotenv import load_dotenv
import os
import urllib

load_dotenv(".env")
_username = urllib.parse.quote(os.getenv("user"))
_password = urllib.parse.quote(os.getenv("password"))

client = MongoClient(
    "mongo.exceed19.online", port=8443, username=_username, password=_password
)
