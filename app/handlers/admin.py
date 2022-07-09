# -*- coding: UTF-8 -*-
from models.newsletter import Newsletter
from models.link import Link
from models.database import Database
from services import links_service, newsletter_service
from repositories import links_repo
from flask import Blueprint, redirect, request
from flask_login import login_required
import json
import logging 
from dateutil import parser

admin = Blueprint('admin', __name__)
from datetime import date, datetime


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
    for newsletter in Newsletter.list():
        news = newsletter.to_dict()
        news['links'] = [link.to_dict() for link in links_repo.by_newsletter(newsletter.key)]
        data['newsletters'].append(news)
    for link in Link.drafts():
        data['drafts'].append(link.to_dict())
    for link in Link.queued():
        data['queue'].append(link.to_dict())
    for link in Link.toread():
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
        n.save()
        key = n.key()
        logging.info(u"Create newsletter {} - {}".format(n.number, n.title))
        for l in nl['links']:
            link = Link.from_dict(l)
            link.newsletter = key
            
            link.save()
            logging.info(u"Create link {}".format(link.title))
    for l in data['queue']:
        link = Link.from_dict(l)
        link.save()
    for l in data['drafts']:
        link = Link.from_dict(l)
        link.save()
    for l in data['readinglist']:
        link = Link.from_dict(l)
        link.save()

    return "OK"


@admin.route('/migrate', methods=['POST'])
def migrate():
    for newsletter in Database.db.collection(Newsletter.collection).stream():
        d = newsletter.to_dict()
        if isinstance(d['stored'], str):
            stored = datetime.fromisoformat(d['stored'])
            Database.db.collection(Newsletter.collection).document(newsletter.id).update({'stored': stored})
        if isinstance(d['sentdate'], str):
            stored = datetime.fromisoformat(d['sentdate'])
            Database.db.collection(Newsletter.collection).document(newsletter.id).update({'sentdate': stored})
    return "OK"
