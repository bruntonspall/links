# -*- coding: UTF-8 -*-
import logging

from flask import Flask
from models import Newsletter, Link, Settings
from flask import request, render_template, redirect, url_for
from flaskext.markdown import Markdown
import requests_toolbelt.adapters.appengine

from handlers.admin import admin
from handlers.newsletter import newsletter
from handlers.links import links
from handlers.fetch import fetch


requests_toolbelt.adapters.appengine.monkeypatch()

app = Flask(__name__)
Markdown(app)

@app.route('/')
def index():
    nl = Newsletter.most_recent_published()
    return render_template("front.html", newsletter=nl, links=Link.by_newsletter(nl.key), newsletters=Newsletter.list())

@app.route('/<newsletterslug>')
def newsletter(newsletterslug):
    nl = Newsletter.by_slug(newsletterslug)
    if nl:
        return render_template("front.html", newsletter=nl, links=Link.by_newsletter(nl.key), newsletters=Newsletter.list())
    else:
        return 'No such newsletter',404



@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
