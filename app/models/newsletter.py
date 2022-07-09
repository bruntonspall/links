from .database import Database
from datetime import datetime
from google.cloud import firestore
from slugify import slugify


class Newsletter:
    collection = u"newsletters"

    def __init__(self, title=None, body=None, slug=None, sent=False, number=None, sentdate=None):
        self.title = title
        self.body = body
        self.slug = slug
        self.sent = sent
        self.number = number
        self.stored = datetime.now()
        self.updated = datetime.now()
        if sent:
            self.sentdate = sentdate

    @staticmethod
    def from_dict(source):
        n = Newsletter(number=source['number'])
        n.title = source.get('title', None)
        n.body = source.get('body', None)
        n.slug = source.get('slug', None)
        n.sent = source.get('sent', None)
        n.stored = source.get('stored', None)
        n.updated = source.get('updated', None)
        if 'sentdate' in source:
            if isinstance(source['sentdate'], str):
                n.sentdate = datetime.fromisoformat(source['sentdate'])
            else:
                n.sentdate = source['sentdate']
        return n

    def to_dict(self):
        d = {
            'title': self.title,
            'body': self.body,
            'slug': self.slug,
            'number': self.number,
            'stored': self.stored,
            'updated': self.updated,
            'sent': self.sent
        }
        if self.sent:
            d['sentdate'] = self.sentdate
        return d

    def save(self):
        self.updated = datetime.now()
        Database.getDb().collection(Newsletter.collection).document(self.key()).set(self.to_dict())

    def key(self):
        return str(self.number)

    def delete(self):
        # for link in Link.by_newsletter(self.key()):
        #     link.newsletter = None
        #     link.save()
        Database.getDb().collection(Newsletter.collection).document(self.key()).delete()

    @staticmethod
    def first(query):
        docs = query.limit(1).stream()
        doc = next(docs, None)
        if doc:
            return Newsletter.from_dict(doc.to_dict())
        return None

    @staticmethod
    def _list():
        return Database.getDb().collection(Newsletter.collection).order_by(u"updated", direction=firestore.Query.DESCENDING)

    @staticmethod
    def list():
        return [Newsletter.from_dict(d.to_dict()) for d in Newsletter._list().stream()]

    @staticmethod
    def _list_published():
        return Database.getDb().collection(Newsletter.collection).where(u"sent", "==", True).order_by(u"sentdate", direction=firestore.Query.DESCENDING)

    @staticmethod
    def list_published():
        return [Newsletter.from_dict(d.to_dict()) for d in Newsletter._list_published().stream()]

    @staticmethod
    def most_recent():
        return Newsletter.first(Newsletter._list())

    @staticmethod
    def most_recent_published():
        return Newsletter.first(Newsletter._list_published())

    @staticmethod
    def by_number(number):
        return Newsletter.first(Database.getDb().collection(Newsletter.collection).where(u"number", "==", number))

    @staticmethod
    def by_slug(slug):
        return Newsletter.first(Database.getDb().collection(Newsletter.collection).where(u"slug", "==", slug))

    @staticmethod
    def get(key):
        return Newsletter.from_dict(Database.getDb().collection(Newsletter.collection).document(key).get().to_dict())

    def slugify(self):
        if not self.title:
            return "untitled"
        if not self.slug:
            self.slug = slugify(self.title)
        return self.slug

    def set_sent(self):
        self.sent = True
        self.sentdate = datetime.now()
