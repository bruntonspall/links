from os import environ
from models import Newsletter, Link, Settings
from flask import request, render_template, redirect, url_for, Blueprint
import requests
import json
import twitter
import flask.json
import datetime
import logging
from fetchutils import notion_richtext_to_markdown
from notion_client import Client
import google.cloud.logging



fetch = Blueprint('fetch', __name__)
logging_client = google.cloud.logging.Client()
logger = logging_client.logger("fetch")
logging_client.setup_logging()



@fetch.route("/")
def fetch_index():
    settings = {
        "pinboard_auth": Settings.get('PINBOARD_TOKEN'),
        "pinboard_last": Settings.get('PINBOARD_LAST', default=None),
        "consumerkey": Settings.get('TWITTER_CONSUMER_KEY'),
        "consumersecret": Settings.get('TWITTER_CONSUMER_SECRET'),
        "accesskey": Settings.get('TWITTER_ACCESS_KEY'),
        "accesssecret": Settings.get('TWITTER_ACCESS_SECRET'),
        "twitter_last": Settings.get('TWITTER_LAST', default=None),
        "notion_auth": Settings.get('NOTION_TOKEN'),
        "notion_db": Settings.get('NOTION_DB'),
        "notion_tag": Settings.get('NOTION_TAG'),
        "notion_last": Settings.get('NOTION_LASTRUN', default=None)
    }
    logging.info(settings)
    return render_template("fetch.html", settings=settings)


@fetch.route("/settings/pinboard", methods=["POST"])
def update_pinboard_settings():
    Settings.set('PINBOARD_TOKEN', request.values.get('pinboard_auth'))
    return redirect("/admin/fetch/")


@fetch.route("/settings/twitter", methods=["POST"])
def update_twitter_settings():
    Settings.set('TWITTER_CONSUMER_KEY', request.values.get('consumerkey'))
    Settings.set('TWITTER_CONSUMER_SECRET', request.values.get('consumersecret'))
    Settings.set('TWITTER_ACCESS_KEY', request.values.get('accesskey'))
    Settings.set('TWITTER_ACCESS_SECRET', request.values.get('accesssecret'))
    return redirect("/admin/fetch/")


@fetch.route("/settings/notion", methods=["POST"])
def update_notion_settings():
    Settings.set('NOTION_TOKEN', request.values.get('notion_auth'))
    Settings.set('NOTION_DB', request.values.get('notion_db'))
    Settings.set('NOTION_TAG', request.values.get('notion_tag'))
    return redirect("/admin/fetch/")


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
                ).save()
                count += 1
    logging.info(f"Processed {count} items")
    return redirect("/admin/fetch/")


@fetch.route('/notion')
def fetch_notion():
    authtoken = Settings.get('NOTION_TOKEN')
    tag = Settings.get('NOTION_TAG', default="CyberWeeklyImport")
    db = Settings.get('NOTION_DB')
    lastrun = Settings.get('NOTION_LASTRUN', default=None)
    logging.info(f"Fetching from notion {db} with token {authtoken}")
    notion = Client(auth=authtoken)

    if lastrun:
        since = {"after": lastrun}
    else:
        since = {"past_week": {}}

    importtime = datetime.datetime.now().isoformat()
    count = 0

    # Process items that have been editing in the last week, but already tagged
    query = {
        "and": [
            {"property": "Edited", "date": since},
        ]}
    logging.info(f"Fetching from Notion with query {query}")

    existing_items = notion.databases.query(database_id=db, filter=query)

    for result in existing_items["results"]:
        if "Imported" in result["properties"] and result["properties"]["Imported"]["date"]:
            lastimported = datetime.datetime.fromisoformat(result["properties"]["Imported"]["date"]["start"])
        else:
            lastimported = datetime.datetime.fromisoformat("1999-01-01T00:00:00.000+00:00")
        edited = datetime.datetime.fromisoformat(result["properties"]["Edited"]["last_edited_time"].replace('Z', '+00:00'))
        name = result['properties']['Name']['title'][0]['plain_text']
        logging.info(f"Examining {name} - Edited {edited}, imported {lastimported}")

        if edited > lastimported:  # Has it been touched in Notion since we last ran the import script?
            url = result['properties']['URL']['url']
            logger.log_struct({"entry": url, "NotionObject": result})
            comment = notion_richtext_to_markdown(result['properties']['Comment']['rich_text'])
            quote = notion_richtext_to_markdown(result['properties']['Quote']['rich_text'])
            title = notion_richtext_to_markdown(result['properties']['Name']['title'])
            existing = Link.get_by_url(url)
            if not existing:
                Link(
                    url=url,
                    title=title,
                    quote=quote,
                    note=comment,
                    type=0
                ).save()
                count += 1
                logging.info(f"Creating {name}")
                tags = result['properties']['Tags']
                if filter(lambda t: t["name"] == tag, tags["multi_select"]):
                    tags['multi_select'].append({'name': tag})
                imported = {"date": {"start": importtime}}
                print(f"Setting imported to {importtime}")
                notion.pages.update(page_id=result['id'], properties={'Tags': tags, 'Imported': imported})
            else:
                # We've seen this before somewhere, so we need to work out whether to update it or not
                # Never touch live links, or links that are in a newsletter
                if existing.type == Link.SENT or existing.newsletter:
                    logging.info(f"{name} was already sent in newsletter {existing.newsletter}")
                else:
                    if existing.stored > edited:
                        logging.info(f"{name} was updated in Cyberweekly({existing.stored}) more recently than in Notion {edited}")
                    else:
                        existing.title = title
                        existing.quote = quote
                        existing.note = comment
                        existing.save()
                        count += 1
                        tags = result['properties']['Tags']
                        if filter(lambda t: t["name"] == tag, tags["multi_select"]):
                            tags['multi_select'].append({'name': tag})
                        imported = {"date": {"start": importtime}}
                        print(f"Updated, so setting Imported to {importtime}")
                        notion.pages.update(page_id=result['id'], properties={'Tags': tags, 'Imported': imported})
        else:
            logging.info("Hasn't been edited since importing, so skipping")

    Settings.set('NOTION_LASTRUN', importtime)
    logging.info(f"Processed {count} items")
    return redirect("/admin/fetch/")


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
