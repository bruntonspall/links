from flask import request, render_template, redirect, url_for, Blueprint
from models import Newsletter, Link, Settings
from datetime import date, datetime
import logging


newsletter = Blueprint('newsletter', __name__)

@newsletter.route('/create', methods=['POST'])
def create_newsletter():
    if request.values.get('number'):
        number = request.values.get('number')
    else:
        old = Newsletter.most_recent()
        number = 1
        if old:
            number = str(int(old.number)+1)
    newsletter = Newsletter(number=number).put()
    for link in Link.queued():
        link.newsletter = newsletter
        link.put()
    return redirect('/newsletter/{}'.format(newsletter.urlsafe()))


@newsletter.route('/<newsletterid>', methods=['GET'])
def get_newsletter(newsletterid):
    newsletter = Newsletter.get(newsletterid)
    return render_template("newsletter.html", newsletter=newsletter, links=Link.by_newsletter(newsletter.key))

@newsletter.route('/<newsletterid>/send', methods=['POST'])
def send_newsletter(newsletterid):
    newsletter = Newsletter.get(newsletterid)
    newsletter.url = request.values.get('url')
    newsletter.sent = date.today()
    newsletter.put()
    for link in Link.by_newsletter(newsletter.key):
        link.type = Link.SENT
        link.put()

    return redirect('/newsletter/{}'.format(newsletterid))

@newsletter.route('/<newsletterid>/edit', methods=['GET', 'POST'])
def edit_newsletter(newsletterid):
    newsletter = Newsletter.get(newsletterid)
    if request.method == 'POST':
        logging.error("Edit with values {}".format(request.values))
        if request.values.get('sent') != None and request.values.get('sent') != 'None':
            if newsletter.sent == None:
                return send_newsletter(newsletterid)
            else:
                newsletter.sent = datetime.strptime(request.values.get('sent'), '%Y-%m-%d').date()
        newsletter.title = request.values.get('title')
        newsletter.intro = request.values.get('intro')
        newsletter.number = request.values.get('number')
        newsletter.put()
        return redirect('/')
    return render_template('edit_newsletter.html', newsletter=newsletter)
