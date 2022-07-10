from models.link import Link
from repositories import settings_repo, links_repo, newsletter_repo
from flask import request, render_template, redirect, Blueprint
import requests
import twitter
import datetime
import logging
from fetchutils import notion_richtext_to_markdown
from notion_client import Client
fetch = Blueprint('fetch', __name__)


@fetch.route("/")
def fetch_index():
    settings = {
        "pinboard_auth": settings_repo.get('PINBOARD_TOKEN'),
        "pinboard_last": settings_repo.get('PINBOARD_LAST', default=None),
        "consumerkey": settings_repo.get('TWITTER_CONSUMER_KEY'),
        "consumersecret": settings_repo.get('TWITTER_CONSUMER_SECRET'),
        "accesskey": settings_repo.get('TWITTER_ACCESS_KEY'),
        "accesssecret": settings_repo.get('TWITTER_ACCESS_SECRET'),
        "twitter_last": settings_repo.get('TWITTER_LAST', default=None),
        "notion_auth": settings_repo.get('NOTION_TOKEN'),
        "notion_db": settings_repo.get('NOTION_DB'),
        "notion_tag": settings_repo.get('NOTION_TAG'),
        "notion_last": settings_repo.get('NOTION_LASTRUN', default=None)
    }
    logging.info(settings)
    return render_template("fetch.html", settings=settings)


@fetch.route("/settings/pinboard", methods=["POST"])
def update_pinboard_settings():
    settings_repo.set('PINBOARD_TOKEN', request.values.get('pinboard_auth'))
    return redirect("/admin/fetch/")


@fetch.route("/settings/twitter", methods=["POST"])
def update_twitter_settings():
    settings_repo.set('TWITTER_CONSUMER_KEY', request.values.get('consumerkey'))
    settings_repo.set('TWITTER_CONSUMER_SECRET', request.values.get('consumersecret'))
    settings_repo.set('TWITTER_ACCESS_KEY', request.values.get('accesskey'))
    settings_repo.set('TWITTER_ACCESS_SECRET', request.values.get('accesssecret'))
    return redirect("/admin/fetch/")


@fetch.route("/settings/notion", methods=["POST"])
def update_notion_settings():
    settings_repo.set('NOTION_TOKEN', request.values.get('notion_auth'))
    settings_repo.set('NOTION_DB', request.values.get('notion_db'))
    settings_repo.set('NOTION_TAG', request.values.get('notion_tag'))
    return redirect("/admin/fetch/")


@fetch.route('/pinboard')
def fetch_pinboard():
    authtoken = settings_repo.get('PINBOARD_TOKEN')
    lastfetch = settings_repo.get('PINBOARD_LAST')
    logging.error("Fetching api with token {}".format(authtoken))

    dt = requests.get('https://api.pinboard.in/v1/posts/update', params={
        'format': 'json',
        'auth_token': authtoken,
    }).json()
    if 'update_time' in dt and dt['update_time'] != lastfetch:
        settings_repo.set('PINBOARD_LAST', dt['update_time'])
        d = requests.get('http://api.pinboard.in/v1/posts/all', params={
            'format': 'json',
            'results': '75',
            'tag': 'newsletter',
            'auth_token': authtoken
        }).json()
        count = 0
        for item in d:
            if not links_repo.get_by_url(item['href']):
                links_repo.save(Link(
                    url=item['href'],
                    title=item['description'],
                    note=item['extended'],
                    type=0
                ))
                count += 1
    logging.info(f"Processed {count} items")
    return redirect("/admin/fetch/")


@fetch.route('/notion')
def fetch_notion():
    authtoken = settings_repo.get('NOTION_TOKEN')
    tag = settings_repo.get('NOTION_TAG', default="CyberWeeklyImport")
    db = settings_repo.get('NOTION_DB')
    lastrun = settings_repo.get('NOTION_LASTRUN', default=None)
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
            # logger.log_struct({"entry": url, "NotionObject": result})
            comment = notion_richtext_to_markdown(result['properties']['Comment']['rich_text'])
            quote = notion_richtext_to_markdown(result['properties']['Quote']['rich_text'])
            title = notion_richtext_to_markdown(result['properties']['Name']['title'])
            existing = links_repo.get_by_url(url)
            if not existing:
                links_repo.save(Link(
                    url=url,
                    title=title,
                    quote=quote,
                    note=comment,
                    type=0
                ))
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
                if existing.type == links_repo.SENT or existing.newsletter:
                    logging.info(f"{name} was already sent in newsletter {existing.newsletter}")
                else:
                    if existing.stored > edited:
                        logging.info(f"{name} was updated in Cyberweekly({existing.stored}) more recently than in Notion {edited}")
                    else:
                        existing.title = title
                        existing.quote = quote
                        existing.note = comment
                        links_repo.save(existing)
                        count += 1
                        tags = result['properties']['Tags']
                        if filter(lambda t: t["name"] == tag, tags["multi_select"]):
                            tags['multi_select'].append({'name': tag})
                        imported = {"date": {"start": importtime}}
                        print(f"Updated, so setting Imported to {importtime}")
                        notion.pages.update(page_id=result['id'], properties={'Tags': tags, 'Imported': imported})
        else:
            logging.info("Hasn't been edited since importing, so checking if it's gone live")
            existing = links_repo.get_by_url(url)
            if existing:  # This is in the database, is it live?
                if existing.type == links_repo.SENT and existing.newsletter:
                    newsletter = newsletter_repo.get(existing.newsletter)
                    issuetag = "CyberWeekly" + newsletter.number
                    tags = result['properties']['Tags']
                    if filter(lambda t: t["name"] == issuetag, tags["multi_select"]):
                        tags['multi_select'].append({'name': issuetag})
                    notion.pages.update(page_id=result['id'], properties={'Tags': tags})

    settings_repo.set('NOTION_LASTRUN', importtime)
    logging.info(f"Processed {count} items")
    return redirect("/admin/fetch/")


@fetch.route('/twitter')
def fetch_twitter_favs():
    consumerkey = settings_repo.get('TWITTER_CONSUMER_KEY')
    consumersecret = settings_repo.get('TWITTER_CONSUMER_SECRET')
    accesskey = settings_repo.get('TWITTER_ACCESS_KEY')
    accesssecret = settings_repo.get('TWITTER_ACCESS_SECRET')
    lastfetch = settings_repo.get('TWITTER_LAST', default="")
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
                    if not links_repo.get_by_url(u.expanded_url):
                        links_repo.save(Link(
                            url=u.expanded_url,
                            title=fav.text,
                            note="Tweet: [https://twitter.com/{}/status{}]()".format(fav.user.screen_name, fav.id),
                            type=0
                        ))
                        count += 1
        settings_repo.set('TWITTER_LAST', favs[0].id_str)
    return 'Processed {} items'.format(count)
