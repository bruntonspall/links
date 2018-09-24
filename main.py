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

app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(newsletter, url_prefix='/newsletter')
app.register_blueprint(links, url_prefix='/link')
app.register_blueprint(fetch, url_prefix='/fetch')

@app.route('/')
def index():
    return render_template("list.html", newsletters=Newsletter.list(), queue=Link.queued(), links=Link.drafts().fetch())


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
