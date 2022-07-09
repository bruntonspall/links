from flask import request, render_template, redirect, url_for, Blueprint, abort
from services import newsletter_service
from models.newsletter import Newsletter
from models.link import Link
from datetime import date, datetime
from flask_login import login_required
import logging


newsletter = Blueprint('newsletter', __name__)


@newsletter.route('/create', methods=['POST'])
@login_required
def create_newsletter():
    nl = newsletter_service.create_newsletter(number=request.values.get('number'))
    return redirect('/admin/newsletter/{}'.format(nl.key()))


@newsletter.route('/<newsletterid>', methods=['GET'])
@login_required
def get_newsletter(newsletterid):
    newsletter = Newsletter.get(newsletterid)
    return render_template("newsletter.html", newsletter=newsletter, links=Link.by_newsletter(newsletter.key()))


@newsletter.route('/<newsletterid>/send', methods=['POST'])
@login_required
def send_newsletter(newsletterid):
    url = request.values.get('url')
    newsletter_service.send(newsletterid, url)

    return redirect('/admin/newsletter/{}'.format(newsletterid))


@newsletter.route('/<newsletterid>/delete', methods=['POST'])
@login_required
def delete_newsletter(newsletterid):
    newsletter_service.delete(newsletterid)
    return redirect('/admin/index')


@newsletter.route('/<newsletterid>/edit', methods=['GET', 'POST'])
@login_required
def edit_newsletter(newsletterid):
    newsletter = Newsletter.get(newsletterid)
    if request.method == 'POST':
        newsletter.title = request.values.get('title')
        newsletter.body = request.values.get('body')
        newsletter.number = request.values.get('number')
        newsletter.slugify()
        newsletter.save()
        return redirect('/admin/newsletter/{}'.format(newsletterid))
    return render_template('edit_newsletter.html', newsletter=newsletter)
