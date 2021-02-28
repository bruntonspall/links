from google.cloud import firestore
from slugify import slugify
from datetime import datetime
from flask_login import UserMixin
import uuid


class Database:
    db = firestore.Client()

class User(UserMixin):
    collection = "Users"
    def __init__(self, id_, email, name, picture):
        self.id = id_
        self.email = email
        self.name = name
        self.picture = picture

    @staticmethod
    def from_dict(source):
        return User(id_=source['id'], email=source['email'], name=source['name'], picture=source['picture'])

    @staticmethod
    def get(user_id):
        docref = Database.db.collection(User.collection).document(user_id).get()
        if not docref.exists:
            return None
        return User.from_dict(docref.to_dict())

    @staticmethod
    def create(id_, email, name, picture):
        userdict = {
            'id':id_,
            'email':email,
            'name':name,
            'picture':picture
        }
        Database.db.collection(User.collection).document(id_).set(userdict)
        return User.from_dict(userdict)

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
        n.title=source.get('title', None)
        n.body=source.get('body', None)
        n.slug=source.get('slug', None)
        n.sent=source.get('sent', None)
        n.stored = source.get('stored', None)
        n.updated = source.get('updated', None)
        if 'sentdate' in source:
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
        Database.db.collection(Newsletter.collection).document(self.key()).set(self.to_dict())

    def key(self):
        return str(self.number)

    def delete(self):
        for link in Link.by_newsletter(self.key()):
            link.newsletter = None
            link.save()
        Database.db.collection(Newsletter.collection).document(self.key()).delete()
        

    @staticmethod
    def first(query):
        docs = query.limit(1).stream()
        doc = next(docs, None)
        if doc:
            return Newsletter.from_dict(doc.to_dict())
        return None

    @staticmethod
    def _list():
        return Database.db.collection(Newsletter.collection).order_by(u"updated", direction=firestore.Query.DESCENDING)

    @staticmethod
    def list():
        return [Newsletter.from_dict(d.to_dict()) for d in Newsletter._list().stream()]

    @staticmethod
    def _list_published():
        return Database.db.collection(Newsletter.collection).where(u"sent", "==", True).order_by(u"sentdate", direction=firestore.Query.DESCENDING)

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
        return Newsletter.first(Database.db.collection(Newsletter.collection).where(u"number", "==", number))

    @staticmethod
    def by_slug(slug):
        return Newsletter.first(Database.db.collection(Newsletter.collection).where(u"slug", "==", slug))

    @staticmethod
    def get(key):
        return Newsletter.from_dict(Database.db.collection(Newsletter.collection).document(key).get().to_dict())

    def slugify(self):
        if not self.title:
            return "untitled"
        if not self.slug:
            self.slug = slugify(self.title)
        return self.slug

    def set_sent(self):
        self.sent = True
        self.sentdate = datetime.now()


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
        self.stored = datetime.now()
        self.updated = datetime.now()
        self.url = url
        self.type = type
        self.title = title
        self.note = note
        self.quote = quote
        self.source = source
        self.newsletter = newsletter

    @staticmethod
    def from_dict(source):
        l = Link(url=source['url'], type=source['type'],title=source['title'],note=source['note'],quote=source['quote'],source=source['source'])
        l.key = source.get('key', str(uuid.uuid4()))
        l.stored = source['stored']
        l.updated = source['updated']
        l.newsletter = source.get('newsletter', None)
        return l

    @staticmethod
    def first(query):
        docs = query.limit(1).stream()
        doc = next(docs, None)
        if doc:
            return Link.from_dict(doc.to_dict())
        return None

    def save(self):
        self.updated = datetime.now()
        Database.db.collection(Link.collection).document(self.key).set(self.to_dict())

    @staticmethod
    def query():
        return Database.db.collection(Link.collection)

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


class Settings:
    collection = u"settings"

    @staticmethod
    def get(name, default="NOT SET"):
        retval = Database.db.collection(Settings.collection).document(name).get()
        if not retval.exists:
            Database.db.collection(Settings.collection).document(name).set({
                "name": name,
                "value": default
            })
            return default
        return retval.to_dict()["value"]

    @staticmethod
    def set(name, value):
        Database.db.collection(Settings.collection).document(name).set({
            "name": name,
            "value": value
        })
