# -*- coding: UTF-8 -*-
import logging
import os
import requests
import json

from flask import Flask
from models import Database, Newsletter, Link, User
from flask import render_template, request, url_for, redirect
from flaskext.markdown import Markdown

from handlers.admin import admin
from handlers.newsletter import newsletter
from handlers.links import links
from handlers.fetch import fetch

from datetime import timedelta
from flask_login import (
    LoginManager,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient

app = Flask(__name__)
Markdown(app)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)


app.register_blueprint(admin, url_prefix='/admin/admin')
app.register_blueprint(newsletter, url_prefix='/admin/newsletter')
app.register_blueprint(links, url_prefix='/admin/link')
app.register_blueprint(fetch, url_prefix='/admin/fetch')


# Configuration
GOOGLE_CLIENT_ID = os.environ.get("OAUTH_CLIENTID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("OAUTH_CLIENTSECRET", None)
GOOGLE_CALLBACK = os.environ.get("OAUTH_CALLBACK", "https://www.cyberweekly.net/login/callback")

GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
client = WebApplicationClient(GOOGLE_CLIENT_ID)

ALLOWED_USERS = ["michael@brunton-spall.co.uk", "joel@slash32.co.uk"]


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/admin/index')
@login_required
def adminindex():
    return render_template("adminlist.html", newsletters=Newsletter.list(), queue=Link.queued(), links=Link.drafts())


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=GOOGLE_CALLBACK,
        scope=["openid", "email"],
    )
    logging.warning(f"Redirecting to {request_uri}")
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Hack to replace http:// with https:// in request.url and request.base_url
    url = request.url.replace('http://', 'https://')
    base_url = request.base_url.replace('http://', 'https://')
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=url,
        redirect_url=base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    logging.warn(f"token Response {token_response.json()}")
    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    logging.warn(f"userinfo Response {userinfo_response.json()}")
    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json().get("picture", None)
        users_name = userinfo_response.json().get("given_name", users_email)
    else:
        return "User email not available or not verified by Google.", 400

    # Check whether user is in list of allowed users
    if users_email not in ALLOWED_USERS:
        return "Users email is not in the allow-list"

    # Create a user in your db with the information provided
    # by Google

    # Doesn't exist? Add it to the database.
    user = User.get(unique_id)
    if not user:
        user = User.create(unique_id, users_email, users_name, picture)

    # Begin user session by logging the user in
    login_user(user, remember=True, duration=timedelta(days=6))
    next = request.args.get('next')
    logging.warn(f"next: {next}")

    # Send user back to homepage
    return redirect("/admin/index")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route('/admin/readinglist')
@login_required
def reading():
    return render_template("readinglist.html", newsletters=Newsletter.list(), readinglist=Link.toread())


@app.route('/')
def index():
    nl = Newsletter.most_recent_published()
    if not nl:
        nl = Newsletter(title="DEBUG NEWSLETTER", body="DEBUG DEBUG, DEBUG", number=-1)
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
    if os.environ.get("LOCALDB", False):
        from mockfirestore import MockFirestore
        Database.db = MockFirestore()
        app.config['LOGIN_DISABLED'] = True
    app.run(debug=True, threaded=True, host='0.0.0.0',
            port=int(os.environ.get('PORT', 8080)))
