from flask import request, render_template, redirect, url_for, Blueprint
from models import *
from datetime import date, datetime
from auth import check_user
import logging


newsletter = Blueprint('newsletter', __name__)
newsletter.before_request(check_user)


@newsletter.route('/create', methods=['POST'])
def create_newsletter():
    if request.values.get('number'):
        number = request.values.get('number')
    else:
        old = NewsletterDraft.most_recent()
        number = 1
        if old:
            number = old.id+1
    newsletter = NewsletterDraft(id=number)
    newsletter.put()
    for link in Link.queued_in_reverse():
        dp = PlacementDraft.from_link(link)
        newsletter.add_placement(dp)
    return redirect('/admin/newsletter/{}'.format(newsletter.key.urlsafe()))


@newsletter.route('/<newsletterid>', methods=['GET'])
def get_newsletter(newsletterid):
    newsletter = NewsletterDraft.get(newsletterid)
    return render_template("newsletter.html", newsletter=newsletter, links=newsletter.placements(), newsletters=NewsletterDraft.list())


@newsletter.route('/<newsletterid>/send', methods=['POST'])
def send_newsletter(newsletterid):
    newsletter = NewsletterDraft.get(newsletterid)
    newsletter.url = request.values.get('url')
    newsletter.sent = date.today()
    newsletter.put()
    livenewsletter = newsletter.launch()
    for lp in livenewsletter.placements():
        link = Link.get_by_url(lp.url)
        link.type = Link.SENT
        link.put()

    return redirect('/admin/newsletter/{}'.format(newsletterid))


@newsletter.route('/<newsletterid>/delete', methods=['POST'])
def delete_newsletter(newsletterid):
    newsletter = NewsletterDraft.get(newsletterid)
    for dp in newsletter.placements():
        dp.key.delete()
    newsletter.key.delete()
    return redirect('/admin/index')


@newsletter.route('/<newsletterid>/takedown', methods=['POST'])
def takedown_newsletter(newsletterid):
    newsletter = NewsletterDraft.get(newsletterid)
    ln = newsletter.live_newsletter.get()
    for lp in ln.placements():
        lp.key.delete()
    ln.key.delete()
    newsletter.live_newsletter = None
    newsletter.dirty = 0
    newsletter.put()
    return redirect('/admin/newsletter/{}'.format(newsletterid))



@newsletter.route('/<newsletterid>/edit', methods=['GET', 'POST'])
def edit_newsletter(newsletterid):
    newsletter = NewsletterDraft.get(newsletterid)
    if request.method == 'POST':
        logging.error("Edit with values {}".format(request.values))
        if request.values.get('sent') != None and request.values.get('sent') != 'None':
            if newsletter.sent == None:
                return send_newsletter(newsletterid)
            else:
                newsletter.sent = datetime.strptime(request.values.get('sent'), '%Y-%m-%d').date()
        newsletter.title = request.values.get('title')
        newsletter.slugify()
        newsletter.intro = request.values.get('intro')
        newsletter.id = int(request.values.get('id'))
        newsletter.dirty = 1
        newsletter.put()
        return redirect('/admin/newsletter/{}'.format(newsletterid))
    return render_template('edit_newsletter.html', newsletter=newsletter, newsletters=NewsletterDraft.list())
