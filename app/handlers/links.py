# -*- coding: UTF-8 -*-
from flask import request, render_template, redirect, url_for, Blueprint
from models import Newsletter, Link, Settings
from flask_login import login_required
import logging

links = Blueprint('links', __name__)


@links.route('/<linkid>')
@login_required
def show_link(linkid):
    link = Link.get(linkid)
    return render_template("view.html", link=link)

@links.route('/<linkid>/edit', methods=['GET', 'POST'])
@login_required
def edit_link(linkid):
    logging.info(f"Getting link {linkid}")
    link = Link.get(linkid)
    if request.method == 'POST':
        link.title = request.form.get('title', link.title)
        link.quote = request.form.get('quote', link.quote)
        link.note = request.form.get('note', link.note)
        link.url = request.form.get('url', link.title)
        link.type = int(request.form.get('linktype', link.type))
        todraft = request.form.get('todraft', None)
        if todraft:
            link.type = Link.DRAFT

        link.save()
        return redirect('/admin/index')
    return render_template("form.html", link=link)


@links.route('/<linkid>/read')
@login_required
def read_link(linkid):
    link = Link.get(linkid)
    link.type = Link.DRAFT
    link.save()
    return redirect('/admin/readinglist')


@links.route('/<linkid>/unread')
@login_required
def unread_link(linkid):
    link = Link.get(linkid)
    link.type = Link.TOREAD
    link.save()
    return redirect('/admin/index')


@links.route('/<linkid>/queue')
@login_required
def queue_link(linkid):
    link = Link.get(linkid)
    link.type = Link.QUEUED
    link.save()
    return redirect('/admin/index')


@links.route('/<linkid>/dequeue')
@login_required
def dequeue_link(linkid):
    link = Link.get(linkid)
    link.type = Link.DRAFT
    link.save()
    return redirect('/admin/index')


@links.route('/<linkid>/delete')
@login_required
def delete_link(linkid):
    link = Link.delete(linkid)
    return redirect('/admin/index')


@links.route('/add', methods=['GET'])
@login_required
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
@login_required
def add_post():
    url = request.form.get('url')
    link = Link.get_by_url(url)
    if link == None:
        link = Link(url=url, type=Link.TOREAD)
    link.title = request.form.get('title', link.title)
    link.quote = request.form.get('quote', link.quote)
    link.note = request.form.get('note', link.note)
    link.type = int(request.form.get('linktype', link.type))
    todraft = request.form.get('todraft', None)
    if todraft:
        link.type = Link.DRAFT
    link.save()
    return render_template('form.html', link=link)