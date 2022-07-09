from models.link import Link
from repositories import links_repo


def mark_read(linkid):
    link = links_repo.get(linkid)
    link.type = Link.DRAFT
    link.save()


def mark_unread(linkid):
    link = links_repo.get(linkid)
    link.type = Link.TOREAD
    link.save()


def queue(linkid):
    link = links_repo.get(linkid)
    link.type = Link.QUEUED
    link.save()


def dequeue(linkid):
    link = links_repo.get(linkid)
    link.type = Link.DRAFT
    link.save()


def delete(linkid):
    links_repo.delete(linkid)


def create(link):
    links_repo.create(link)


def get(linkid):
    return links_repo.get(linkid)


def get_by_url(url):
    return links_repo.get_by_url(url)
