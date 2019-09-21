# -*- coding: UTF-8 -*-
from models import Newsletter, Link, Settings
from flask import Blueprint, redirect, request
import json
import logging 
from dateutil import parser

admin = Blueprint('admin', __name__)


@admin.route('/testdata')
def testdata():
    link = Link(url='http://www.iso27001security.com/html/27000.html',
                type=Link.DRAFT,
                title='ISMS/ISO27k overview section',
                quote='I wish the committee would replace “information security risk” throughout ISO27k with the simpler and more appropriate term “information risk”.',
                note='A note').put()
    link = Link(url='https://www.riskiq.com/blog/labs/magecart-british-airways-breach/',
                type=Link.DRAFT,
                title='Inside the Magecart Breach of British Airways: How 22 Lines of Code Claimed 380,000 Victims',
                quote='On September 6th, British Airways announced it had suffered a breach resulting in the theft of customer data. In interviews with the BBC, the company noted that around 380,000 customers could have been affected and that the stolen information included personal and payment information but not passport information. ',
                note='A note').put()

    newsletter = Newsletter(number='1').put()
    for link in Link.queued():
        link.newsletter = newsletter
        link.put()
    return redirect('/admin/index')


@admin.route('/export')
def export():
    data = {
        'newsletters':[],
        'queue':[],
        'readinglist':[],
        'drafts':[]
    }
    for newsletter in Newsletter.list():
        news = newsletter.to_json()
        news['links'] = [link.to_json() for link in Link.by_newsletter(newsletter.key)]
        data['newsletters'].append(news)
    for link in Link.drafts():
        data['drafts'].append(link.to_json())
    for link in Link.queued():
        data['queue'].append(link.to_json())
    for link in Link.toread():
        data['readinglist'].append(link.to_json())

    return json.dumps(data, indent=4)

@admin.route('/import', methods=['POST'])
def imp():
    data = request.json['json']
    for nl in data['newsletters']:
        logging.info(u"Parsing {}".format(nl))
        n = Newsletter(
            stored = parser.parse(nl['stored']),
            updated = parser.parse(nl['updated']),
            url = nl['url'],
            title = nl['title'],
            intro = nl['intro'],
            sent = parser.parse(nl['sent']),
            number = nl['number']
        )
        n.slugify()
        key = n.put()
        logging.info(u"Create newsletter {} - {}".format(n.number, n.title))
        for l in nl['links']:
            link = Link(
                note = l['note'],
                quote = l['quote'],
                source = l['source'],
                title = l['title'],
                type = l['type'],
                url = l['url'],
                stored = parser.parse(l['stored']),
                updated = parser.parse(l['updated'])
            )
            link.newsletter = key
            
            link.put()
            logging.info(u"Create link {}".format(link.title))
    for l in data['queue']:
        link = Link(
                note = l['note'],
                quote = l['quote'],
                source = l['source'],
                title = l['title'],
                type = l['type'],
                url = l['url'],
                stored = parser.parse(l['stored']),
                updated = parser.parse(l['updated'])
            ).put()
    for l in data['drafts']:
        link = Link(
                note = l['note'],
                quote = l['quote'],
                source = l['source'],
                title = l['title'],
                type = l['type'],
                url = l['url'],
                stored = parser.parse(l['stored']),
                updated = parser.parse(l['updated'])
            ).put()
    for l in data['readinglist']:
        link = Link(
                note = l['note'],
                quote = l['quote'],
                source = l['source'],
                title = l['title'],
                type = l['type'],
                url = l['url'],
                stored = parser.parse(l['stored']),
                updated = parser.parse(l['updated'])
            ).put()

    return "OK"