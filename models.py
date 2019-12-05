from google.appengine.ext import ndb
from slugify import slugify


class Newsletter(ndb.model.Model):
    stored = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    url = ndb.StringProperty()
    title = ndb.StringProperty()
    intro = ndb.TextProperty()
    sent = ndb.DateProperty()
    number = ndb.StringProperty()
    slug = ndb.StringProperty()

    def to_json(self):
        return {
            'stored': self.stored.isoformat(),
            'updated': self.updated.isoformat(),
            'url': self.url,
            'title': self.title,
            'intro': self.intro,
            'sent': self.sent.isoformat(),
            'number': self.number,
            'slug': self.slug
        }

    @classmethod
    def list(cls):
        return cls.query().order(-Newsletter.sent).order(-Newsletter.number)

    @classmethod
    def list_published(cls):
        return cls.query(Newsletter.sent != None).order(-Newsletter.sent).order(-Newsletter.number)

    @classmethod
    def most_recent(cls):
        return cls.query().order(-Newsletter.sent).order(-Newsletter.number).fetch()[0]

    @classmethod
    def most_recent_published(cls):
        return cls.query(Newsletter.sent != None).order(-Newsletter.sent).order(-Newsletter.number).fetch()[0]

    @classmethod
    def by_number(cls, number):
        return cls.query(Newsletter.number == number).get()

    @classmethod
    def by_slug(cls, slug):
        return cls.query(Newsletter.slug == slug).get()

    @classmethod
    def get(cls, key):
        return ndb.Key(urlsafe=key).get()

    def slugify(self):
        if not self.title:
            return "untitled"
        if not self.slug:
            self.slug = slugify(self.title)
        return self.slug


class Link(ndb.model.Model):
    TOREAD = 0
    DRAFT = 1
    QUEUED = 2
    SENT = 3
    DELETED = 4

    stored = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    url = ndb.StringProperty(required=True)
    type = ndb.IntegerProperty(required=True)
    title = ndb.StringProperty()
    note = ndb.TextProperty()
    quote = ndb.TextProperty()
    source = ndb.StringProperty()
    newsletter = ndb.KeyProperty(kind=Newsletter)

    def note_paras(self):
        return self.note.split('\n')

    def to_json(self):
        return {
            'stored': self.stored.isoformat(),
            'updated': self.updated.isoformat(),
            'url': self.url,
            'type': self.type,
            'title': self.title,
            'note': self.note,
            'quote': self.quote,
            'source': self.source
        }

    @classmethod
    def get_by_url(cls, url):
        return cls.query(Link.url == url).get()

    @classmethod
    def get(cls, key):
        return ndb.Key(urlsafe=key).get()

    @classmethod
    def delete(cls, key):
        link = ndb.Key(urlsafe=key).get()
        link.type = Link.DELETED
        link.put()
        return None

    @classmethod
    def toread(cls):
        return cls.query(Link.type == cls.TOREAD).order(-Link.updated)

    @classmethod
    def drafts(cls):
        return cls.query(Link.type == cls.DRAFT).order(-Link.updated).fetch()

    @classmethod
    def queued(cls):
        return cls.query(Link.type == cls.QUEUED).order(-Link.updated).fetch()

    @classmethod
    def queued_in_reverse(cls):
        return cls.query(Link.type == cls.QUEUED).order(Link.updated)

    @classmethod
    def by_newsletter(cls, newsletter):
        return cls.query(Link.newsletter == newsletter).order(-Link.updated)

    @classmethod
    def by_newsletter_in_reverse(cls, newsletter):
        return cls.query(Link.newsletter == newsletter).order(Link.updated)

class Settings(ndb.Model):
    name = ndb.StringProperty()
    value = ndb.StringProperty()

    @staticmethod
    def get(name, default="NOT SET"):
        retval = Settings.query(Settings.name == name).get()
        if not retval:
            retval = Settings()
            retval.name = name
            retval.value = default
            retval.put()
        return retval.value

    @staticmethod
    def set(name, value):
        retval = Settings.query(Settings.name == name).get()
        if not retval:
            retval = Settings()
            retval.name = name
        retval.value = value
        retval.put()
