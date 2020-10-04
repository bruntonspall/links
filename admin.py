# -*- coding: UTF-8 -*-
import logging

from flask import Flask
from models import *
from flask import request, render_template, redirect, url_for, g
from flaskext.markdown import Markdown
import requests_toolbelt.adapters.appengine

from handlers.admin import admin
from handlers.newsletter import newsletter
from handlers.links import links
from handlers.fetch import fetch

from google.appengine.api import users

from auth import login_required, check_user

requests_toolbelt.adapters.appengine.monkeypatch()

app = Flask(__name__)
Markdown(app)

app.register_blueprint(admin, url_prefix='/admin/admin')
app.register_blueprint(newsletter, url_prefix='/admin/newsletter')
app.register_blueprint(links, url_prefix='/admin/link')
app.register_blueprint(fetch, url_prefix='/admin/fetch')



@app.route('/admin/index')
@login_required
def index():
    return render_template("adminlist.html", newsletters=NewsletterDraft.list(), queue=Link.queued(), links=Link.drafts())

@app.route('/admin/readinglist')
@login_required
def reading():
    return render_template("readinglist.html", newsletters=NewsletterDraft.list(), readinglist=Link.toread())


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500
