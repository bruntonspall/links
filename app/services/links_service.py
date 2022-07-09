from repositories import links_repo


def mark_read(linkid):
    link = links_repo.get(linkid)
    link.type = links_repo.DRAFT
    links_repo.save(link)


def mark_unread(linkid):
    link = links_repo.get(linkid)
    link.type = links_repo.TOREAD
    links_repo.save(link)


def queue(linkid):
    link = links_repo.get(linkid)
    link.type = links_repo.QUEUED
    links_repo.save(link)


def dequeue(linkid):
    link = links_repo.get(linkid)
    link.type = links_repo.DRAFT
    links_repo.save(link)


def delete(linkid):
    links_repo.delete(linkid)


def create(link):
    links_repo.create(link)


def get(linkid):
    return links_repo.get(linkid)


def get_by_url(url):
    return links_repo.get_by_url(url)
