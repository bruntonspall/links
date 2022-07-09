from models.newsletter import Newsletter
from google.cloud import firestore
from models.database import Database
from datetime import datetime


def first(query):
    docs = query.limit(1).stream()
    doc = next(docs, None)
    if doc:
        return Newsletter.from_dict(doc.to_dict())
    return None


def _list():
    return Database.getDb().collection(Newsletter.collection).order_by(u"updated", direction=firestore.Query.DESCENDING)


def list():
    return [Newsletter.from_dict(d.to_dict()) for d in _list().stream()]


def _list_published():
    return Database.getDb().collection(Newsletter.collection).where(u"sent", "==", True).order_by(u"sentdate", direction=firestore.Query.DESCENDING)


def list_published():
    return [Newsletter.from_dict(d.to_dict()) for d in _list_published().stream()]


def most_recent():
    return first(_list())


def most_recent_published():
    return first(_list_published())


def by_number(number):
    return first(Database.getDb().collection(Newsletter.collection).where(u"number", "==", number))


def by_slug(slug):
    return first(Database.getDb().collection(Newsletter.collection).where(u"slug", "==", slug))


def get(key):
    return Newsletter.from_dict(Database.getDb().collection(Newsletter.collection).document(key).get().to_dict())


def save(newletter, update_time=True):
    if update_time:
        newletter.updated = datetime.now()
    Database.getDb().collection(Newsletter.collection).document(newletter.key()).set(newletter.to_dict())


def delete(newletter):
    Database.getDb().collection(Newsletter.collection).document(newletter.key()).delete()
