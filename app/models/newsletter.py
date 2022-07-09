from datetime import datetime
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

    def key(self):
        return str(self.number)

    def slugify(self):
        if not self.title:
            return "untitled"
        if not self.slug:
            self.slug = slugify(self.title)
        return self.slug

    def set_sent(self):
        self.sent = True
        self.sentdate = datetime.now()
