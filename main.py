# -*- coding: UTF-8 -*-
import logging

from flask import Flask
from models import *
from flask import render_template
from flaskext.markdown import Markdown
import requests_toolbelt.adapters.appengine


requests_toolbelt.adapters.appengine.monkeypatch()

app = Flask(__name__)
Markdown(app)


@app.route('/')
def index():
    nl = NewsletterLive.most_recent()
    return render_template("front/index.html", newsletter=NewsletterLive.most_recent(), newsletters=NewsletterLive.list_published())


@app.route('/<newsletterslug>')
def newsletter(newsletterslug):
    nl = NewsletterLive.by_slug(newsletterslug)
    if nl:
        return render_template("front/newsletter.html", newsletter=nl, links=nl.placements(), newsletters=NewsletterLive.list_published())
    else:
        return 'No such newsletter', 404


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
