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
    version = ndb.IntegerProperty(default=1)

    def to_json(self):
        return {
            'stored': self.stored.isoformat(),
            'updated': self.updated.isoformat(),
            'url': self.url,
            'title': self.title,
            'intro': self.intro,
            'sent': self.sent.isoformat(),
            'number': self.number,
            'slug': self.slug,
            'version': self.version
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


class NewsletterLive(ndb.model.Model):
    id = ndb.IntegerProperty()
    stored = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    sent = ndb.DateProperty()
    url = ndb.StringProperty()
    title = ndb.StringProperty()
    intro = ndb.TextProperty()
    slug = ndb.StringProperty()

    def to_json(self):
        return {
            'id': self.id,
            'stored': self.stored.isoformat(),
            'updated': self.updated.isoformat(),
            'sent': self.sent.isoformat(),
            'url': self.url,
            'title': self.title,
            'intro': self.intro,
            'slug': self.slug
        }

    @classmethod
    def list(cls):
        return cls.query().order(-cls.id)

    @classmethod
    def list_published(cls):
        return cls.query().order(-cls.id)

    @classmethod
    def most_recent(cls):
        return cls.query().order(-cls.id).fetch()[0]

    @classmethod
    def by_number(cls, id):
        return cls.query(cls.id == id).get()

    @classmethod
    def by_slug(cls, slug):
        return cls.query(cls.slug == slug).get()

    @classmethod
    def get(cls, key):
        return ndb.Key(urlsafe=key).get()

    def slugify(self):
        if not self.title:
            return "untitled"
        if not self.slug:
            self.slug = slugify(self.title)
        return self.slug

    def placements(self):
        return PlacementLive.query(PlacementLive.newsletter == self.key).order(-PlacementLive.updated).fetch()

    def live(self):
        return True


class NewsletterDraft(ndb.model.Model):
    id = ndb.IntegerProperty()
    stored = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    sent = ndb.DateProperty()
    url = ndb.StringProperty()
    title = ndb.StringProperty()
    intro = ndb.TextProperty()
    slug = ndb.StringProperty()
    dirty = ndb.IntegerProperty(default=1)
    live_newsletter = ndb.KeyProperty(NewsletterLive)

    def to_json(self):
        return {
            'id': self.id,
            'stored': self.stored.isoformat(),
            'updated': self.updated.isoformat(),
            'sent': self.sent.isoformat(),
            'url': self.url,
            'title': self.title,
            'intro': self.intro,
            'slug': self.slug
        }

    @classmethod
    def list(cls):
        return cls.query().order(-cls.id)

    @classmethod
    def list_published(cls):
        return None

    @classmethod
    def most_recent(cls):
        return cls.query().order(-cls.id).fetch()[0]

    @classmethod
    def by_number(cls, id):
        return cls.query(cls.id == id).get()

    @classmethod
    def by_slug(cls, slug):
        return cls.query(cls.slug == slug).get()

    @classmethod
    def get(cls, key):
        return ndb.Key(urlsafe=key).get()

    def slugify(self):
        if not self.title:
            return "untitled"
        if not self.slug:
            self.slug = slugify(self.title)
        return self.slug
    
    def add_placement(self, placement):
        id = len(placement.__class__.query(placement.__class__.newsletter == self.key).fetch())+1
        placement.newsletter = self.key
        placement.id = id
        placement.put()

    def placements(self):
        return PlacementDraft.query(PlacementDraft.newsletter == self.key).order(-PlacementDraft.updated).fetch()

    def launch(self):
        newsletter = NewsletterLive.by_number(self.id)
        if not newsletter:
            newsletter = NewsletterLive()
        newsletter.id=self.id 
        newsletter.url=self.url
        newsletter.title=self.title
        newsletter.intro=self.intro
        newsletter.slug=self.slug
        newsletter.sent=self.sent
        newsletter.updated=self.updated
        newsletter.put()
        for placement in PlacementDraft.query(PlacementDraft.newsletter == self.key).order(PlacementDraft.updated):
            placement.launch(newsletter)
        self.live_newsletter = newsletter.key
        self.dirty = 0
        self.put()
        return newsletter
    
    def live(self):
        return False


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
        return cls.query(Link.type == cls.TOREAD).order(-Link.updated).fetch()

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

class PlacementLive(ndb.model.Model):
    id = ndb.IntegerProperty()
    updated = ndb.DateTimeProperty(auto_now=True)
    title = ndb.StringProperty()
    quote = ndb.TextProperty()
    note = ndb.TextProperty()
    url = ndb.StringProperty(required=True)
    order = ndb.IntegerProperty()
    link = ndb.KeyProperty(kind=Link)
    newsletter = ndb.KeyProperty(kind=NewsletterLive)

    def note_paras(self):
        return self.note.split('\n')

    def to_json(self):
        return {
            'order':self.order,
            'updated': self.updated.isoformat(),
            'title': self.title,
            'quote': self.quote,
            'note': self.note,
            'url': self.url,
        }

    @classmethod
    def get_by_newsletter_id(cls, newsletter, id):
        return cls.query(cls.newsletter == newsletter).filter(cls.id == id).get()

    @classmethod
    def get(cls, key):
        return ndb.Key(urlsafe=key).get()

    @classmethod
    def delete(cls, key):
        link = ndb.Key(urlsafe=key).get()
        link.delete()
        return None

    @classmethod
    def by_newsletter(cls, newsletter):
        return cls.query(cls.newsletter == newsletter).order(cls.order)

    @classmethod
    def by_newsletter_in_reverse(cls, newsletter):
        return cls.query(cls.newsletter == newsletter).order(-cls.order)

class PlacementDraft(ndb.model.Model):
    id = ndb.IntegerProperty()
    updated = ndb.DateTimeProperty(auto_now=True)
    title = ndb.StringProperty()
    quote = ndb.TextProperty()
    note = ndb.TextProperty()
    url = ndb.StringProperty(required=True)
    order = ndb.IntegerProperty()
    link = ndb.KeyProperty(kind=Link)
    live = ndb.KeyProperty(kind=PlacementLive)
    newsletter = ndb.KeyProperty(kind=NewsletterDraft)

    def note_paras(self):
        return self.note.split('\n')

    def to_json(self):
        return {
            'id': self.id,
            'order':self.order,
            'updated': self.updated.isoformat(),
            'title': self.title,
            'quote': self.quote,
            'note': self.note,
            'url': self.url,
        }

    @classmethod
    def get_by_url(cls, url):
        return cls.query(cls.url == url).fetch()

    @classmethod
    def get(cls, key):
        return ndb.Key(urlsafe=key).get()

    @classmethod
    def delete(cls, key):
        link = ndb.Key(urlsafe=key).get()
        link.delete()
        return None

    @classmethod
    def by_newsletter(cls, newsletter):
        return cls.query(cls.newsletter == newsletter).order(cls.order)

    @classmethod
    def by_newsletter_in_reverse(cls, newsletter):
        return cls.query(cls.newsletter == newsletter).order(-cls.order)

    @classmethod
    def from_link(cls, link):
        placement = cls(
            # No order yet
            title = link.title,
            quote = link.quote,
            note = link.note,
            url = link.url,
            link = link.key
        )
        placement.put()
        return placement
    
    def launch(self, livenewsletter):
        placement = PlacementLive.get_by_newsletter_id(livenewsletter.key, self.id)
        if not placement:
            placement = PlacementLive()
        placement.id=self.id
        placement.order=self.order
        placement.title=self.title
        placement.quote=self.quote
        placement.note=self.note
        placement.url=self.url
        placement.updated=self.updated
        placement.newsletter=livenewsletter.key
        placement.link=self.link
        placement.put()
        self.live = placement.key
        self.put()
        return placement

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
