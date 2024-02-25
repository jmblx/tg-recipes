import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

ADMIN_LIST = (os.getenv('ADMIN_LIST')).split(",")
