from datetime import datetime
import unittest
from models.database import Database
from models.newsletter import Newsletter
from models.link import Link
from services import newsletter_service
from mockfirestore import MockFirestore


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        Database.db = MockFirestore()

    def tearDown(self):
        Database.db.reset()


class UserServiceTestCase(DatabaseTestCase):
    pass


class NewsletterServiceTestCase(DatabaseTestCase):
    def create_test_data(self):
        live_newsletter = Newsletter("Newsletter 1", "This is newsletter 1")
        live_newsletter.number = 1
        live_newsletter.stored = datetime.fromisoformat("2020-03-06 13:00")
        live_newsletter.updated = datetime.fromisoformat("2020-03-06 13:00")
        live_newsletter.sent = True
        live_newsletter.sentdate = datetime.fromisoformat("2020-03-06 13:00")
        live_newsletter.slugify()
        live_newsletter.save()

        Link(url="http://foo.com/link1", type=Link.SENT, newsletter=live_newsletter).save()
        Link(url="http://foo.com/link2", type=Link.SENT, newsletter=live_newsletter).save()
        Link(url="http://foo.com/link2", type=Link.SENT, newsletter=live_newsletter).save()

        draft_newsletter = Newsletter("Newsletter 2", "Some body text")
        draft_newsletter.number = 2
        draft_newsletter.stored = datetime.fromisoformat("2020-03-07 13:00")
        draft_newsletter.updated = datetime.fromisoformat("2020-03-07 13:00")
        draft_newsletter.sent = True
        draft_newsletter.sentdate = datetime.fromisoformat("2020-03-07 13:00")
        draft_newsletter.slugify()
        draft_newsletter.save()

        Link(url="http://foo.com/link4", type=Link.SENT, newsletter=draft_newsletter).save()
        Link(url="http://foo.com/link5", type=Link.SENT, newsletter=draft_newsletter).save()
        Link(url="http://foo.com/link6", type=Link.SENT, newsletter=draft_newsletter).save()

        self.queuedlink = Link(url="http://foo.com/link7", type=Link.QUEUED)
        self.queuedlink.save()
        self.draftlink = Link(url="http://foo.com/link8", type=Link.DRAFT)
        self.draftlink.save()

    def test_create_newsletter(self):
        self.create_test_data()
        self.assertEqual(len(Newsletter.list()), 2)
        self.assertEqual(self.queuedlink.newsletter, None)
        self.assertEqual(self.draftlink.newsletter, None)
        nl = newsletter_service.create_newsletter()
        self.assertEqual(len(Newsletter.list()), 3)
        self.assertEqual(nl.number, '3')
        links = Link.by_newsletter(nl.key())

        self.assertEqual(len(links), 1)
        self.assertEqual(links[0].url, self.queuedlink.url)

