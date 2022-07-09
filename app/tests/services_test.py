from datetime import datetime
import unittest
from models.database import Database
from models.newsletter import Newsletter
from models.link import Link
from services import newsletter_service
from repositories import newsletter_repo, links_repo
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
        newsletter_repo.save(live_newsletter)

        links_repo.save(Link(url="http://foo.com/link1", type=links_repo.SENT, newsletter=live_newsletter))
        links_repo.save(Link(url="http://foo.com/link2", type=links_repo.SENT, newsletter=live_newsletter))
        links_repo.save(Link(url="http://foo.com/link2", type=links_repo.SENT, newsletter=live_newsletter))

        draft_newsletter = Newsletter("Newsletter 2", "Some body text")
        draft_newsletter.number = 2
        draft_newsletter.stored = datetime.fromisoformat("2020-03-07 13:00")
        draft_newsletter.updated = datetime.fromisoformat("2020-03-07 13:00")
        draft_newsletter.sent = True
        draft_newsletter.sentdate = datetime.fromisoformat("2020-03-07 13:00")
        draft_newsletter.slugify()
        newsletter_repo.save(draft_newsletter)

        links_repo.save(Link(url="http://foo.com/link4", type=links_repo.SENT, newsletter=draft_newsletter))
        links_repo.save(Link(url="http://foo.com/link5", type=links_repo.SENT, newsletter=draft_newsletter))
        links_repo.save(Link(url="http://foo.com/link6", type=links_repo.SENT, newsletter=draft_newsletter))

        self.queuedlink = Link(url="http://foo.com/link7", type=links_repo.QUEUED)
        links_repo.save(self.queuedlink)
        self.draftlink = Link(url="http://foo.com/link8", type=links_repo.DRAFT)
        links_repo.save(self.draftlink)

    def test_create_newsletter(self):
        self.create_test_data()
        self.assertEqual(len(newsletter_repo.list()), 2)
        self.assertEqual(self.queuedlink.newsletter, None)
        self.assertEqual(self.draftlink.newsletter, None)
        nl = newsletter_service.create_newsletter()
        self.assertEqual(len(newsletter_repo.list()), 3)
        self.assertEqual(nl.number, '3')
        links = links_repo.by_newsletter(nl.key())

        self.assertEqual(len(links), 1)
        self.assertEqual(links[0].url, self.queuedlink.url)

