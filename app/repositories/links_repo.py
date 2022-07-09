from models.link import Link
from models.database import Database
from google.cloud import firestore
from datetime import datetime, timezone


TOREAD = 0
DRAFT = 1
QUEUED = 2
SENT = 3
DELETED = 4


def first(query):
    docs = query.limit(1).stream()
    doc = next(docs, None)
    if doc:
        return Link.from_dict(doc.to_dict())
    return None


def create(link):
    save(link)


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
    return [Link.from_dict(d.to_dict()) for d in query().where("type", "==", TOREAD).order_by("updated", firestore.Query.DESCENDING).stream()]


def drafts():
    return [Link.from_dict(d.to_dict()) for d in query().where("type", "==", DRAFT).order_by("updated", firestore.Query.DESCENDING).stream()]


def queued():
    return [Link.from_dict(d.to_dict()) for d in query().where("type", "==", QUEUED).order_by("updated", firestore.Query.DESCENDING).stream()]


def queued_in_reverse():
    return [Link.from_dict(d.to_dict()) for d in query().where("type", "==", QUEUED).order_by("updated").stream()]


def by_newsletter(newsletter):
    return [Link.from_dict(d.to_dict()) for d in query().where("newsletter", "==", newsletter).order_by("updated", firestore.Query.DESCENDING).stream()]


def by_newsletter_in_reverse(newsletter):
    return [Link.from_dict(d.to_dict()) for d in query().where("newsletter", "==", newsletter).order_by("updated").stream()]


def save(link):
    link.updated = datetime.now(timezone.utc)
    Database.getDb().collection(Link.collection).document(link.key).set(link.to_dict())
