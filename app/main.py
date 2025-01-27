# -*- coding: UTF-8 -*-
import logging
import os
import requests
import json

from flask import Flask
from models.newsletter import Newsletter
from models.link import Link
from models.database import Database
from flask import render_template, request, url_for, redirect

from repositories import links_repo, newsletter_repo, user_repo, settings_repo

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

from markupsafe import Markup
from markdown import markdown


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)


app.register_blueprint(admin, url_prefix='/admin/admin')
app.register_blueprint(newsletter, url_prefix='/admin/newsletter')
app.register_blueprint(links, url_prefix='/admin/link')
app.register_blueprint(fetch, url_prefix='/admin/fetch')

@app.template_filter('markdown')
def markup_markdown(text):
    return Markup(markdown(text))

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


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return user_repo.get(user_id)


@app.route('/admin/index')
@login_required
def adminindex():
    return render_template("adminlist.html", newsletters=newsletter_repo.list(), queue=links_repo.queued(), links=links_repo.drafts())


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route('/admin/debuglogin')
def debug_login():
    if app.config['LOGIN_DEBUG']:
        user = user_repo.create("testuser", "test@test.com", "Test User", "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80")
        login_user(user)
    return redirect("/admin/index")

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
    ALLOWED_USERS = settings_repo.get("ALLOWED_USERS").split(",")
    if users_email not in ALLOWED_USERS:
        return "Users email is not in the allow-list"

    # Create a user in your db with the information provided
    # by Google

    # Doesn't exist? Add it to the database.
    user = user_repo.get(unique_id)
    if not user:
        user = user_repo.create(unique_id, users_email, users_name, picture)

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
    return render_template("readinglist.html", newsletters=newsletter_repo.list(), readinglist=links_repo.toread())


@app.route('/')
def index():
    nl = newsletter_repo.most_recent_published()
    if not nl:
        nl = Newsletter(title="DEBUG NEWSLETTER", body="DEBUG DEBUG, DEBUG", number=-1)
    return render_template("front/index.html", newsletter=nl)


@app.route('/archive')
def archive():
    nl = newsletter_repo.most_recent_published()
    if not nl:
        nl = Newsletter(title="DEBUG NEWSLETTER", body="DEBUG DEBUG, DEBUG", number=-1)
    return render_template("front/archive.html", newsletter=nl, newsletters=newsletter_repo.list_published())


@app.route('/<newsletterslug>')
def newsletter(newsletterslug):
    nl = newsletter_repo.by_slug(newsletterslug)
    if nl:
        return render_template("front/newsletter.html", newsletter=nl, links=links_repo.by_newsletter(nl.key()), newsletters=newsletter_repo.list_published())
    else:
        return 'No such newsletter', 404


@app.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    logging.exception('An error occurred during a request.')
    return 'An internal error occurred.', 500


def import_from_file(fname):
    import json
    data = json.load(open(fname))
    for nl in data['newsletters']:
        # Change up the sent fields
        if nl['sent']:
            nl['sentdate'] = nl['sent']
            nl['sent'] = True

        n = Newsletter.from_dict(nl)
        n.body = nl['intro']
        n.slugify()
        newsletter_repo.save(n)
        key = n.key()
        for sublink in nl['links']:
            link = Link.from_dict(sublink)
            link.newsletter = key
            links_repo.save(link)
    for sublink in data['queue']:
        link = Link.from_json(sublink)
        links_repo.save(link)
    for sublink in data['drafts']:
        link = Link.from_json(sublink)
        links_repo.save(link)
    for sublink in data['readinglist']:
        link = Link.from_json(sublink)
        links_repo.save(link)


def debug():
    logging.error("Starting up in local development mode")
    logging.root.level = logging.INFO
    from mockfirestore import MockFirestore
    Database.db = MockFirestore()

    # app.config['LOGIN_DISABLED'] = True
    app.config['LOGIN_DEBUG'] = True

    import os
    if os.path.exists("export.json"):
        import_from_file("export.json")


if __name__ == '__main__':
    debug()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))