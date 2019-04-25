# -*- coding: UTF-8 -*-
import logging

from flask import Flask
from models import Newsletter, Link, Settings
from flask import request, render_template, redirect, url_for, g
from flaskext.markdown import Markdown
import requests_toolbelt.adapters.appengine

from handlers.admin import admin
from handlers.newsletter import newsletter
from handlers.links import links
from handlers.fetch import fetch

from google.appengine.api import users

requests_toolbelt.adapters.appengine.monkeypatch()

app = Flask(__name__)
Markdown(app)

app.register_blueprint(admin, url_prefix='/admin/admin')
app.register_blueprint(newsletter, url_prefix='/admin/newsletter')
app.register_blueprint(links, url_prefix='/admin/link')
app.register_blueprint(fetch, url_prefix='/admin/fetch')

USERS = ["michael@brunton-spall.co.uk", "test@example.com"]

@app.before_request
def check_user():
    user = users.get_current_user()
    g.logout_url = users.create_logout_url('/')
    if user.nickname() not in USERS:
        return "User {} is frobidden from accessing this page, <a href='{}'>logout</a>".format(user.nickname(), g.logout_url), 403


@app.route('/admin/index')
def index():
    return render_template("adminlist.html", newsletters=Newsletter.list(), queue=Link.queued(), links=Link.drafts().fetch(), readinglist=Link.toread())


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
