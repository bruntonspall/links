from flask import request, render_template, redirect, url_for, Blueprint
from models import Newsletter, Link, Settings
from datetime import date, datetime
from auth import check_user
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
    newsletter = Newsletter(number=number)
    newsletter.save()
    for link in Link.queued_in_reverse():
        link.newsletter = newsletter.key()
        link.save()
    return redirect('/admin/newsletter/{}'.format(newsletter.key()))


@newsletter.route('/<newsletterid>', methods=['GET'])
def get_newsletter(newsletterid):
    newsletter = Newsletter.get(newsletterid)
    return render_template("newsletter.html", newsletter=newsletter, links=Link.by_newsletter(newsletter.key()))


@newsletter.route('/<newsletterid>/send', methods=['POST'])
def send_newsletter(newsletterid):
    newsletter = Newsletter.get(newsletterid)
    newsletter.url = request.values.get('url')
    newsletter.sent = True
    newsletter.sentdate = date.today()
    newsletter.save()
    for link in Link.by_newsletter_in_reverse(newsletter.key()):
        link.type = Link.SENT
        link.save()

    return redirect('/admin/newsletter/{}'.format(newsletterid))


@newsletter.route('/<newsletterid>/delete', methods=['POST'])
def delete_newsletter(newsletterid):
    newsletter = Newsletter.get(newsletterid)
    newsletter.key.delete()
    return redirect('/admin/index')


@newsletter.route('/<newsletterid>/edit', methods=['GET', 'POST'])
def edit_newsletter(newsletterid):
    newsletter = Newsletter.get(newsletterid)
    if request.method == 'POST':
        logging.error("Edit with values {}".format(request.values))
        newsletter.title = request.values.get('title')
        newsletter.slugify()
        newsletter.body = request.values.get('body')
        newsletter.number = request.values.get('number')
        newsletter.save()

        if request.values.get('sent') != None and request.values.get('sent') != '':
            if not newsletter.sent:
                return send_newsletter(newsletterid)
            else:
                newsletter.sentdate = datetime.strptime(request.values.get('sent'), '%Y-%m-%d').date()
                newsletter.save()
        return redirect('/admin/newsletter/{}'.format(newsletterid))
    return render_template('edit_newsletter.html', newsletter=newsletter)
