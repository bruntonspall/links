from flask import request, render_template, redirect, url_for, Blueprint
from models import Newsletter, Link, Settings
from datetime import date, datetime
from flask_login import login_required
import logging


newsletter = Blueprint('newsletter', __name__)


@newsletter.route('/create', methods=['POST'])
@login_required
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
@login_required
def get_newsletter(newsletterid):
    newsletter = Newsletter.get(newsletterid)
    return render_template("newsletter.html", newsletter=newsletter, links=Link.by_newsletter(newsletter.key()))


@newsletter.route('/<newsletterid>/send', methods=['POST'])
@login_required
def send_newsletter(newsletterid):
    newsletter = Newsletter.get(newsletterid)
    newsletter.url = request.values.get('url')
    newsletter.sent = True
    newsletter.sentdate = datetime.now()
    newsletter.save()
    for link in Link.by_newsletter_in_reverse(newsletter.key()):
        link.type = Link.SENT
        link.save()

    return redirect('/admin/newsletter/{}'.format(newsletterid))


@newsletter.route('/<newsletterid>/delete', methods=['POST'])
@login_required
def delete_newsletter(newsletterid):
    newsletter = Newsletter.get(newsletterid)
    newsletter.delete()
    return redirect('/admin/index')


@newsletter.route('/<newsletterid>/edit', methods=['GET', 'POST'])
@login_required
def edit_newsletter(newsletterid):
    newsletter = Newsletter.get(newsletterid)
    if request.method == 'POST':
        newsletter.title = request.values.get('title')
        newsletter.slugify()
        newsletter.body = request.values.get('body')
        newsletter.number = request.values.get('number')
        newsletter.save()

        if request.values.get('sent') != None and request.values.get('sent') != '':
            if not newsletter.sent:
                return send_newsletter(newsletterid)
            else:
                newsletter.sentdate = datetime.strptime(request.values.get('sent'), '%Y-%m-%d')
                newsletter.save()
        return redirect('/admin/newsletter/{}'.format(newsletterid))
    return render_template('edit_newsletter.html', newsletter=newsletter)
