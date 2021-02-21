# -*- coding: UTF-8 -*-
from models import Newsletter, Link, Settings
from flask import Blueprint, redirect, request
import json
import logging 
from dateutil import parser

admin = Blueprint('admin', __name__)
from datetime import date, datetime

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

@admin.route('/testdata')
def testdata():
    link = Link(url='http://www.iso27001security.com/html/27000.html',
                type=Link.DRAFT,
                title='ISMS/ISO27k overview section',
                quote='I wish the committee would replace “information security risk” throughout ISO27k with the simpler and more appropriate term “information risk”.',
                note='A note').save()
    link = Link(url='https://www.riskiq.com/blog/labs/magecart-british-airways-breach/',
                type=Link.DRAFT,
                title='Inside the Magecart Breach of British Airways: How 22 Lines of Code Claimed 380,000 Victims',
                quote='On September 6th, British Airways announced it had suffered a breach resulting in the theft of customer data. In interviews with the BBC, the company noted that around 380,000 customers could have been affected and that the stolen information included personal and payment information but not passport information. ',
                note='A note').save()

    newsletter = Newsletter(number='1', title="Test Newsleter 1", body="Body").save()
    for link in Link.queued():
        link.newsletter = newsletter.key()
        link.save()
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
        news = newsletter.to_dict()
        news['links'] = [link.to_dict() for link in Link.by_newsletter(newsletter.key)]
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