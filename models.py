from google.appengine.ext import ndb

class Newsletter(ndb.model.Model):
    stored = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    url = ndb.StringProperty()
    title = ndb.StringProperty()
    intro = ndb.TextProperty()
    sent = ndb.DateProperty()
    number = ndb.StringProperty()

    @classmethod
    def list(cls):
        return cls.query().order(-Newsletter.sent).order(-Newsletter.number)

    @classmethod
    def most_recent(cls):
        return cls.query().order(-Newsletter.sent).order(-Newsletter.number).fetch()[0]

    @classmethod
    def by_number(cls, number):
        return cls.query(Newsletter.number == number).get()

    @classmethod
    def get(cls, key):
        return ndb.Key(urlsafe=key).get()



class Link(ndb.model.Model):
    DRAFT = 1
    QUEUED = 2
    SENT = 3

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

    @classmethod
    def get_by_url(cls, url):
        return cls.query(Link.url == url).get()

    @classmethod
    def get(cls, key):
        return ndb.Key(urlsafe=key).get()

    @classmethod
    def delete(cls, key):
        return ndb.Key(urlsafe=key).delete()

    @classmethod
    def drafts(cls):
        return cls.query(Link.type == cls.DRAFT).order(-Link.updated)

    @classmethod
    def queued(cls):
        return cls.query(Link.type == cls.QUEUED).order(-Link.updated)

    @classmethod
    def by_newsletter(cls, newsletter):
        return cls.query(Link.newsletter == newsletter).order(-Link.updated)


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
