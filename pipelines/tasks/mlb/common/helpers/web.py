import requests
from bs4 import BeautifulSoup


def make_request(url: str, timeout=10) -> BeautifulSoup:
    response = requests.get(url, timeout=timeout)
    assert response.status_code == requests.status_codes.codes['ok']

    return BeautifulSoup(response.content, features='html.parser')
