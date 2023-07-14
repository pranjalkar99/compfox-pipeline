import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
import uvicorn
# from pylogger import Logger
import logging
import shutil
import os
from pymongo.mongo_client import MongoClient



logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s -  %(name)s - %(levelname)s - %(message)s')
logging.warning('This will get logged to a file')
