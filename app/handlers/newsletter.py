from flask import request, render_template, redirect, Blueprint
from services import newsletter_service
from repositories import links_repo, newsletter_repo
from flask_login import login_required


newsletter = Blueprint('newsletter', __name__)


@newsletter.route('/create', methods=['POST'])
@login_required
def create_newsletter():
    nl = newsletter_service.create_newsletter(number=request.values.get('number'))
    return redirect('/admin/newsletter/{}'.format(nl.key()))


@newsletter.route('/<newsletterid>', methods=['GET'])
@login_required
def get_newsletter(newsletterid):
    newsletter = newsletter_repo.get(newsletterid)
    return render_template("newsletter.html", newsletter=newsletter, links=links_repo.by_newsletter(newsletter.key()))


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
    newsletter = newsletter_repo.get(newsletterid)
    if request.method == 'POST':
        newsletter.title = request.values.get('title')
        newsletter.body = request.values.get('body')
        newsletter.number = request.values.get('number')
        newsletter.slugify()
        newsletter_repo.save(newsletter)
        return redirect('/admin/newsletter/{}'.format(newsletterid))
    return render_template('edit_newsletter.html', newsletter=newsletter)
