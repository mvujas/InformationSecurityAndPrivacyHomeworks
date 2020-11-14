import requests
from bs4 import BeautifulSoup

DOMAIN = 'http://0.0.0.0:5001/'

def post_html_soup(url, form_data):
    return BeautifulSoup(
        requests.post(url, data=form_data).content, 
        'html.parser')

def get_html_soup(url):
    return BeautifulSoup(
        requests.get(url).content, 
        'html.parser')