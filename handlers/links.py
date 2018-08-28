from flask import request, render_template, redirect, url_for, Blueprint
from models import Newsletter, Link, Settings

links = Blueprint('links', __name__)


@links.route('/<linkid>')
def show_link(linkid):
    link = Link.get(linkid)
    return render_template("view.html", link=link)

@links.route('/<linkid>/edit', methods=['GET', 'POST'])
def edit_link(linkid):
    link = Link.get(linkid)
    if request.method == 'POST':
        link.title = request.form.get('title', link.title)
        link.quote = request.form.get('quote', link.quote)
        link.note = request.form.get('note', link.note)
        link.put()
        return redirect('/')
    return render_template("form.html", link=link)


@links.route('/<linkid>/queue')
def queue_link(linkid):
    link = Link.get(linkid)
    link.type = Link.QUEUED
    link.put()
    return redirect('/')


@links.route('/<linkid>/dequeue')
def dequeue_link(linkid):
    link = Link.get(linkid)
    link.type = Link.DRAFT
    link.put()
    return redirect('/')


@links.route('/<linkid>/delete')
def delete_link(linkid):
    link = Link.delete(linkid)
    return redirect('/')


@links.route('/add', methods=['GET', 'POST'])
def add():
    url = request.values.get('url')
    link = Link.get_by_url(url)
    if link == None:
        link = Link(url=url, type=Link.DRAFT)
    link.title = request.values.get('title', link.title)
    link.quote = request.values.get('quote', link.quote)
    link.note = request.values.get('note', link.note)
    if request.method == 'POST':
        link.put()
        return redirect('/')
    else:
        return render_template('form.html', link=link)
