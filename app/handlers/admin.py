# -*- coding: UTF-8 -*-
from datetime import date, datetime
from models.newsletter import Newsletter
from models.link import Link
from repositories import links_repo, newsletter_repo
from flask import Blueprint, request
import json
import logging

admin = Blueprint('admin', __name__)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


@admin.route('/export')
def export():
    data = {
        'newsletters': [],
        'queue': [],
        'readinglist': [],
        'drafts': []
    }
    for newsletter in newsletter_repo.list():
        news = newsletter.to_dict()
        news['links'] = [link.to_dict() for link in links_repo.by_newsletter(newsletter.key)]
        data['newsletters'].append(news)
    for link in links_repo.drafts():
        data['drafts'].append(link.to_dict())
    for link in links_repo.queued():
        data['queue'].append(link.to_dict())
    for link in links_repo.toread():
        data['readinglist'].append(link.to_dict())

    return json.dumps(data, indent=4, default=json_serial)


@admin.route('/import', methods=['POST'])
def imp():
    data = request.json['json']
    for nl in data['newsletters']:
        logging.info(u"Parsing {}".format(nl))
        # Change up the sent fields
        if nl['sent']:
            nl['sentdate'] = nl['sent']
            nl['sent'] = True

        n = Newsletter.from_dict(nl)
        n.body = nl['intro']
        n.slugify()
        newsletter_repo.save(n)
        key = n.key()
        logging.info(u"Create newsletter {} - {}".format(n.number, n.title))
        for link_d in nl['links']:
            link = Link.from_dict(link_d)
            link.newsletter = key
            links_repo.save(link)
            logging.info(u"Create link {}".format(link.title))
    for link in data['queue']:
        links_repo.save(Link.from_dict(link))
    for link in data['drafts']:
        links_repo.save(Link.from_dict(link))
    for link in data['readinglist']:
        links_repo.sve(Link.from_dict(link))

    return "OK"
