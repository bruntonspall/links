# -*- coding: UTF-8 -*-
import logging

from flask import Flask
from models import Database, Newsletter, Link
from flask import render_template
from flaskext.markdown import Markdown

from handlers.admin import admin
from handlers.newsletter import newsletter
from handlers.links import links
from handlers.fetch import fetch

app = Flask(__name__)
Markdown(app)

app.register_blueprint(admin, url_prefix='/admin/admin')
app.register_blueprint(newsletter, url_prefix='/admin/newsletter')
app.register_blueprint(links, url_prefix='/admin/link')
app.register_blueprint(fetch, url_prefix='/admin/fetch')



@app.route('/admin/index')
# @login_required
def adminindex():
    return render_template("adminlist.html", newsletters=Newsletter.list(), queue=Link.queued(), links=Link.drafts())

@app.route('/admin/readinglist')
# @login_required
def reading():
    return render_template("readinglist.html", newsletters=Newsletter.list(), readinglist=Link.toread())

@app.route('/')
def index():
    nl = Newsletter.most_recent_published()
    return render_template("front/index.html", newsletter=nl, links=Link.by_newsletter(nl.key()), newsletters=Newsletter.list_published())


@app.route('/<newsletterslug>')
def newsletter(newsletterslug):
    nl = Newsletter.by_slug(newsletterslug)
    if nl:
        return render_template("front/newsletter.html", newsletter=nl, links=Link.by_newsletter(nl.key()), newsletters=Newsletter.list_published())
    else:
        return 'No such newsletter', 404


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500

if __name__ == '__main__':
    import os
    if os.environ.get("LOCALDB",False):
        from mockfirestore import MockFirestore
        Database.db = MockFirestore()
    app.run(debug=True, threaded=True, host='0.0.0.0',
            port=int(os.environ.get('PORT', 8080)))