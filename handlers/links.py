# -*- coding: UTF-8 -*-
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
        return redirect('/admin/index')
    return render_template("form.html", link=link)


@links.route('/<linkid>/read')
def read_link(linkid):
    link = Link.get(linkid)
    link.type = Link.DRAFT
    link.put()
    return redirect('/admin/readinglist')


@links.route('/<linkid>/unread')
def unread_link(linkid):
    link = Link.get(linkid)
    link.type = Link.TOREAD
    link.put()
    return redirect('/admin/index')


@links.route('/<linkid>/queue')
def queue_link(linkid):
    link = Link.get(linkid)
    link.type = Link.QUEUED
    link.put()
    return redirect('/admin/index')


@links.route('/<linkid>/dequeue')
def dequeue_link(linkid):
    link = Link.get(linkid)
    link.type = Link.DRAFT
    link.put()
    return redirect('/admin/index')


@links.route('/<linkid>/delete')
def delete_link(linkid):
    link = Link.delete(linkid)
    return redirect('/admin/index')


@links.route('/add', methods=['GET'])
def add_get():
    url = request.values.get('url')
    link = Link.get_by_url(url)
    if link == None:
        link = Link(url=url, type=Link.TOREAD)
    link.title = request.args.get('title', link.title)
    link.quote = request.args.get('quote', link.quote)
    link.note = request.args.get('note', link.note)
    return render_template('form.html', link=link)


@links.route('/add', methods=['POST'])
def add_post():
    url = request.form.get('url')
    link = Link.get_by_url(url)
    if link == None:
        link = Link(url=url, type=Link.TOREAD)
    link.title = request.form.get('title', link.title)
    link.quote = request.form.get('quote', link.quote)
    link.note = request.form.get('note', link.note)
    link.put()
    return render_template('form.html', link=link)

@links.route('/quickadd', methods=['GET'])
def quickadd_get():
    url = request.values.get('url')
    link = Link.get_by_url(url)
    if link == None:
        link = Link(url=url, type=Link.TOREAD)
    link.title = request.args.get('title', link.title)
    link.quote = request.args.get('quote', link.quote)
    link.put()

    return render_template('form.html', link=link)
