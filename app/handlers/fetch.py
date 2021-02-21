from models import Newsletter, Link, Settings
from flask import request, render_template, redirect, url_for, Blueprint
import requests
import logging
import json
import twitter
import flask.json
from auth import check_user

fetch = Blueprint('fetch', __name__)


@fetch.route('/pinboard')
def fetch_pinboard():
    authtoken = Settings.get('PINBOARD_TOKEN')
    lastfetch = Settings.get('PINBOARD_LAST')
    logging.error("Fetching api with token {}".format(authtoken))

    dt = requests.get('https://api.pinboard.in/v1/posts/update',params={
    'format':'json',
    'auth_token':authtoken,
    }).json()
    if 'update_time' in dt and dt['update_time'] != lastfetch:
        Settings.set('PINBOARD_LAST', dt['update_time'])
        d = requests.get('http://api.pinboard.in/v1/posts/all',params={
            'format':'json',
            'results':'75',
            'tag':'newsletter',
            'auth_token':authtoken
        }).json()
        count = 0
        for item in d:
            if not Link.get_by_url(item['href']):
                Link(
                url=item['href'],
                title=item['description'],
                note=item['extended'],
                type=0
                ).put()
                count += 1
        return 'Processed {} items'.format(count)
    return 'No new items to process'


@fetch.route('/twitter')
def fetch_twitter_favs():
    consumerkey = Settings.get('TWITTER_CONSUMER_KEY')
    consumersecret = Settings.get('TWITTER_CONSUMER_SECRET')
    accesskey = Settings.get('TWITTER_ACCESS_KEY')
    accesssecret = Settings.get('TWITTER_ACCESS_SECRET')
    lastfetch = Settings.get('TWITTER_LAST', default="")
    if not lastfetch:
        lastfetch = 0

    api = twitter.Api(consumer_key=consumerkey,
                  consumer_secret=consumersecret,
                  access_token_key=accesskey,
                  access_token_secret=accesssecret)

    favs = api.GetFavorites(screen_name='bruntonspall', include_entities=True, count=50, since_id=lastfetch)
    count = 0
    if len(favs) > 0:
        for fav in favs:
            for u in fav.urls:
                if not u.expanded_url.startswith("https://twitter.com/"):
                    if not Link.get_by_url(u.expanded_url):
                        Link(
                        url=u.expanded_url,
                        title=fav.text,
                        note="Tweet: [https://twitter.com/{}/status{}]()".format(fav.user.screen_name, fav.id),
                        type=0
                        ).put()
                        count += 1
        Settings.set('TWITTER_LAST', favs[0].id_str)
    return 'Processed {} items'.format(count)
