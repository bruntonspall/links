from datetime import datetime
import pytest
from bs4 import BeautifulSoup
from repositories import newsletter_repo
from models.newsletter import Newsletter
import logging


@pytest.fixture()
def app():
    from main import app, debug
    debug()
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here
    n = Newsletter("Newsletter 1", "Some text")
    n.number = 1
    n.stored = datetime.fromisoformat("2020-03-07 13:00")
    n.updated = datetime.fromisoformat("2020-03-07 13:00")
    n.sent = True
    n.sentdate = datetime.fromisoformat("2020-03-07 13:00")
    n.slugify()
    newsletter_repo.save(n, update_time=False)

    n = Newsletter("Newsletter 2", "Some other text")
    n.number = 2
    n.stored = datetime.fromisoformat("2020-03-08 13:00")
    n.updated = datetime.fromisoformat("2020-03-08 13:00")
    n.sent = True
    n.sentdate = datetime.fromisoformat("2020-03-08 13:00")
    n.slugify()
    newsletter_repo.save(n, update_time=False)

    n = Newsletter("Newsletter 3", "Draft newsletter")
    n.number = 3
    n.stored = datetime.fromisoformat("2020-03-09 13:00")
    n.updated = datetime.fromisoformat("2020-03-09 13:00")
    n.slugify()
    newsletter_repo.save(n)

    yield app

    # clean up / reset resources here


@pytest.fixture()
def client(app):
    return app.test_client()


def test_request_index(client):
    response = client.get("/")
    assert b'<h1 class="font-bold text-4xl mb-6">Cyberweekly</h1>' in response.data


def test_request_archive(client):
    response = client.get("/archive")
    assert b'<a href="/" class="navbar-link">Cyber Weekly</a>' in response.data


def test_request_latest_issue(client):
    response = client.get("/")
    soup = BeautifulSoup(response.data, 'html.parser')
    links = soup.nav.div.find_all('a')
    logging.error(links)
    first = links[1]['href']
    response = client.get(first)
    assert b'<h2 class="headline">Cyberweekly #2 - Newsletter 2</h2>' in response.data
