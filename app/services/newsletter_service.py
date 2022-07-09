from datetime import datetime
from repositories import links_repo, newsletter_repo
from models.newsletter import Newsletter


def create_newsletter(number=None):
    if not number:
        number = str(int(newsletter_repo.most_recent().number) + 1)
    newsletter = Newsletter(number=number)
    newsletter_repo.save(newsletter)
    for link in links_repo.queued_in_reverse():
        link.newsletter = newsletter.key()
        links_repo.save(link)
    return newsletter


def send(newsletterid, url=None):
    newsletter = newsletter_repo.get(newsletterid)
    newsletter.url = url
    newsletter.sent = True
    newsletter.sentdate = datetime.now()
    newsletter_repo.save(newsletter)
    for link in links_repo.by_newsletter_in_reverse(newsletter.key()):
        link.type = links_repo.SENT
        links_repo.save(link)
    return newsletter


def delete(newsletterid):
    newsletter = newsletter_repo.get(newsletterid)
    newsletter_repo.delete(newsletter)
    for link in links_repo.by_newsletter_in_reverse(newsletter.key()):
        link.type = links_repo.QUEUED
        links_repo.save(link)
