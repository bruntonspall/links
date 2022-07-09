from datetime import datetime
from repositories import links_repo
from models.newsletter import Newsletter


def create_newsletter(number=None):
    if not number:
        number = str(int(Newsletter.most_recent().number) + 1)
    newsletter = Newsletter(number=number)
    newsletter.save()
    for link in links_repo.queued_in_reverse():
        link.newsletter = newsletter.key()
        link.save()
    return newsletter


def send(newsletterid, url=None):
    newsletter = Newsletter.get(newsletterid)
    newsletter.url = url
    newsletter.sent = True
    newsletter.sentdate = datetime.now()
    newsletter.save()
    for link in links_repo.by_newsletter_in_reverse(newsletter.key()):
        link.type = links_repo.SENT
        link.save()
    return newsletter


def delete(newsletterid):
    newsletter = Newsletter.get(newsletterid)
    newsletter.delete()
    for link in links_repo.by_newsletter_in_reverse(newsletter.key()):
        link.type = links_repo.QUEUED
        link.save()
