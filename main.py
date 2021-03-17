from configparser import ConfigParser
from Webpage import Webpage


config_object = ConfigParser()
config_object.read("config.ini")
base_url = config_object["INPUT"]["Base_URL"]
date_range = config_object["INPUT"]["Date_range"]


web_page = Webpage(base_url, date_range)
web_page.download_pdf()










