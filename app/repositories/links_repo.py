from models.link import Link
from models.database import Database
from google.cloud import firestore

TOREAD = Link.TOREAD
DRAFT = Link.DRAFT
QUEUED = Link.QUEUED
SENT = Link.SENT
DELETED = Link.DELETED


def first(query):
    docs = query.limit(1).stream()
    doc = next(docs, None)
    if doc:
        return Link.from_dict(doc.to_dict())
    return None


def create(link):
    link.save()


def query():
    return Database.getDb().collection(Link.collection)


def get_by_url(url):
    return first(query().where("url", "==", url))


def get(key):
    return Link.from_dict(query().document(key).get().to_dict())


def delete(key):
    query().document(key).update({
        "type": DELETED
    })


def toread():
    return [Link.from_dict(d.to_dict()) for d in query().where("type", "==", Link.TOREAD).order_by("updated", firestore.Query.DESCENDING).stream()]


def drafts():
    return [Link.from_dict(d.to_dict()) for d in query().where("type", "==", Link.DRAFT).order_by("updated", firestore.Query.DESCENDING).stream()]


def queued():
    return [Link.from_dict(d.to_dict()) for d in query().where("type", "==", Link.QUEUED).order_by("updated", firestore.Query.DESCENDING).stream()]


def queued_in_reverse():
    return [Link.from_dict(d.to_dict()) for d in query().where("type", "==", Link.QUEUED).order_by("updated").stream()]


def by_newsletter(newsletter):
    return [Link.from_dict(d.to_dict()) for d in query().where("newsletter", "==", newsletter).order_by("updated", firestore.Query.DESCENDING).stream()]


def by_newsletter_in_reverse(newsletter):
    return [Link.from_dict(d.to_dict()) for d in query().where("newsletter", "==", newsletter).order_by("updated").stream()]
