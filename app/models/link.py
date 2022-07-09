from datetime import datetime, timezone
import uuid
from .newsletter import Newsletter
from .database import Database
from google.cloud import firestore


class Link:
    TOREAD = 0
    DRAFT = 1
    QUEUED = 2
    SENT = 3
    DELETED = 4

    # stored = ndb.DateTimeProperty(auto_now_add=True)
    # updated = ndb.DateTimeProperty(auto_now=True)
    # url = ndb.StringProperty(required=True)
    # type = ndb.IntegerProperty(required=True)
    # title = ndb.StringProperty()
    # note = ndb.TextProperty()
    # quote = ndb.TextProperty()
    # source = ndb.StringProperty()
    # newsletter = ndb.KeyProperty(kind=Newsletter)

    def note_paras(self):
        return self.note.split('\n')

    def to_dict(self):
        return {
            'key': self.key,
            'stored': self.stored,
            'updated': self.updated,
            'url': self.url,
            'type': self.type,
            'title': self.title,
            'note': self.note,
            'quote': self.quote,
            'source': self.source,
            'newsletter': self.newsletter
        }

    collection = u"links"

    def __init__(self, url, type, title="", note="", quote="", source="", newsletter=None):
        self.key = str(uuid.uuid4())
        self.stored = datetime.now(timezone.utc)
        self.updated = datetime.now(timezone.utc)
        self.url = url
        self.type = type
        self.title = title
        self.note = note
        self.quote = quote
        self.source = source
        self.newsletter = newsletter

    @staticmethod
    def from_dict(source):
        link = Link(url=source['url'], type=source['type'], title=source['title'], note=source['note'], quote=source['quote'], source=source['source'])
        link.key = source.get('key', str(uuid.uuid4()))
        link.stored = source['stored']
        link.updated = source['updated']
        link.newsletter = source.get('newsletter', None)
        return link

    @staticmethod
    def from_json(source):
        link = Link(url=source['url'], type=source['type'], title=source['title'], note=source['note'], quote=source['quote'], source=source['source'])
        link.key = source.get('key', str(uuid.uuid4()))
        link.stored = datetime.fromisoformat(source['stored']).replace(tzinfo=timezone.utc)
        link.updated = datetime.fromisoformat(source['updated']).replace(tzinfo=timezone.utc)
        link.newsletter = source.get('newsletter', None)
        return link

    @staticmethod
    def first(query):
        docs = query.limit(1).stream()
        doc = next(docs, None)
        if doc:
            return Link.from_dict(doc.to_dict())
        return None

    def save(self):
        self.updated = datetime.now(timezone.utc)
        Database.getDb().collection(Link.collection).document(self.key).set(self.to_dict())

    @staticmethod
    def query():
        return Database.getDb().collection(Link.collection)

    @staticmethod
    def get_by_url(url):
        return Link.first(Link.query().where("url", "==", url))

    @staticmethod
    def get(key):
        return Link.from_dict(Link.query().document(key).get().to_dict())

    @staticmethod
    def delete(key):
        Link.query().document(key).update({
            "type": Link.DELETED
        })

    @staticmethod
    def toread():
        return [Link.from_dict(d.to_dict()) for d in Link.query().where("type", "==", Link.TOREAD).order_by("updated", firestore.Query.DESCENDING).stream()]

    @staticmethod
    def drafts():
        return [Link.from_dict(d.to_dict()) for d in Link.query().where("type", "==", Link.DRAFT).order_by("updated", firestore.Query.DESCENDING).stream()]

    @staticmethod
    def queued():
        return [Link.from_dict(d.to_dict()) for d in Link.query().where("type", "==", Link.QUEUED).order_by("updated", firestore.Query.DESCENDING).stream()]

    @staticmethod
    def queued_in_reverse():
        return [Link.from_dict(d.to_dict()) for d in Link.query().where("type", "==", Link.QUEUED).order_by("updated").stream()]

    @staticmethod
    def by_newsletter(newsletter):
        return [Link.from_dict(d.to_dict()) for d in Link.query().where("newsletter", "==", newsletter).order_by("updated", firestore.Query.DESCENDING).stream()]

    @staticmethod
    def by_newsletter_in_reverse(newsletter):
        return [Link.from_dict(d.to_dict()) for d in Link.query().where("newsletter", "==", newsletter).order_by("updated").stream()]

    def get_newsletter(self):
        return Newsletter.get(self.newsletter)
