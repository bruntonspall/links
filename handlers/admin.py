# -*- coding: UTF-8 -*-
from models import Newsletter, Link, Settings
from flask import Blueprint, redirect
from datetime import date

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
    return redirect('/')
