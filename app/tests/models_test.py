import unittest
from mockfirestore import MockFirestore
from models.newsletter import Newsletter
from models.link import Link
from models.database import Database
from repositories import links_repo, newsletter_repo, settings_repo
from datetime import datetime


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        Database.db = MockFirestore()

    def tearDown(self):
        Database.db.reset()


class NewsletterTestCase(DatabaseTestCase):
    def createTestData(self):
        n = Newsletter("Newsletter 1", "Some text")
        n.number = 1
        n.stored = datetime.fromisoformat("2020-03-07 13:00")
        n.updated = datetime.fromisoformat("2020-03-07 13:00")
        n.sent = True
        n.sentdate = datetime.fromisoformat("2020-03-07 13:00")
        n.slugify()
        newsletter_repo.save(n)

        n = Newsletter("Newsletter 2", "Some other text")
        n.number = 2
        n.stored = datetime.fromisoformat("2020-03-08 13:00")
        n.updated = datetime.fromisoformat("2020-03-08 13:00")
        n.sent = True
        n.sentdate = datetime.fromisoformat("2020-03-08 13:00")
        n.slugify()
        newsletter_repo.save(n)

        n = Newsletter("Newsletter 3", "Draft newsletter")
        n.number = 3
        n.stored = datetime.fromisoformat("2020-03-09 13:00")
        n.updated = datetime.fromisoformat("2020-03-09 13:00")
        n.slugify()
        newsletter_repo.save(n)

    def testNewsletter(self):
        actual = Newsletter('Kids in America', 'some text')
        actual.number = 777
        newsletter_repo.save(actual)

        self.assertEqual("777", actual.key())

        retval = Database.db.collection(Newsletter.collection).document("777").get()
        self.assertTrue(retval.exists)
        actual = retval.to_dict()
        self.assertEqual(777, actual['number'])
        self.assertEqual("Kids in America", actual['title'])
        self.assertEqual("some text", actual['body'])
        self.assertEqual(None, actual['slug'])

    def testNewsletterSlugs(self):
        actual = Newsletter("Kids in America", "some text")
        self.assertEqual("Kids in America", actual.title)

        self.assertEqual(None, actual.slug)
        self.assertEqual("kids-in-america", actual.slugify())
        self.assertEqual("kids-in-america", actual.slug)

    def testQueries(self):
        self.createTestData()

        self.assertEqual(3, len(list(newsletter_repo.list())))
        newsletters = [Newsletter.from_dict(d.to_dict()) for d in newsletter_repo.list_published()]
        self.assertEqual(2, len(newsletters))
        self.assertEqual(2, newsletters[0].number)
        self.assertEqual(1, newsletters[1].number)

        self.assertEqual(3, newsletter_repo.most_recent().number)
        self.assertEqual(2, newsletter_repo.most_recent_published().number)

    def testGetByNumber(self):
        self.createTestData()
        n = newsletter_repo.by_number(2)
        self.assertEqual("Newsletter 2", n.title)
        n = newsletter_repo.by_slug("newsletter-1")
        self.assertEqual("Newsletter 1", n.title)
        n = newsletter_repo.get("1")
        self.assertEqual("Newsletter 1", n.title)


class LinkTestCase(DatabaseTestCase):
    def testLink(self):
        actual = Link(url="http://foo.com/something", type=links_repo.TOREAD)
        id = actual.key
        links_repo.save(actual)
        retval = Database.db.collection(Link.collection).document(id).get()
        self.assertTrue(retval.exists)
        actual = retval.to_dict()
        self.assertEqual(id, actual['key'])
        self.assertEqual("http://foo.com/something", actual['url'])
        self.assertEqual(links_repo.TOREAD, actual['type'])

        ret = links_repo.get(id)
        self.assertEqual("http://foo.com/something", ret.url)
        self.assertEqual(id, ret.key)

    def testLinkLifecycle(self):
        self.assertEqual(0, len(list(links_repo.toread())))
        self.assertEqual(0, len(list(links_repo.drafts())))
        self.assertEqual(0, len(list(links_repo.queued())))

        actual = Link(url="http://foo.com/thing", type=links_repo.TOREAD)
        links_repo.save(actual)

        self.assertEqual(1, len(list(links_repo.toread())))
        self.assertEqual(0, len(list(links_repo.drafts())))
        self.assertEqual(0, len(list(links_repo.queued())))

        actual.type = links_repo.DRAFT
        links_repo.save(actual)

        self.assertEqual(0, len(list(links_repo.toread())))
        self.assertEqual(1, len(list(links_repo.drafts())))
        self.assertEqual(0, len(list(links_repo.queued())))

        actual.type = links_repo.QUEUED
        links_repo.save(actual)

        self.assertEqual(0, len(list(links_repo.toread())))
        self.assertEqual(0, len(list(links_repo.drafts())))
        self.assertEqual(1, len(list(links_repo.queued())))

        links_repo.delete(actual.key)

        self.assertEqual(0, len(list(links_repo.toread())))
        self.assertEqual(0, len(list(links_repo.drafts())))
        self.assertEqual(0, len(list(links_repo.queued())))

    def createTestData(self):
        links_repo.save(Link(url="http://foo.com/toread1", type=links_repo.TOREAD))
        links_repo.save(Link(url="http://foo.com/toread2", type=links_repo.TOREAD))
        links_repo.save(Link(url="http://foo.com/draft1", type=links_repo.DRAFT))
        links_repo.save(Link(url="http://foo.com/queued1", type=links_repo.QUEUED))
        links_repo.save(Link(url="http://foo.com/deleted1", type=links_repo.DELETED))

    def testQueries(self):
        self.createTestData()
        self.assertEqual("http://foo.com/toread2", links_repo.toread()[0].url)
        self.assertEqual("http://foo.com/toread1", links_repo.toread()[1].url)
        self.assertEqual("http://foo.com/draft1", links_repo.drafts()[0].url)
        self.assertEqual("http://foo.com/queued1", links_repo.queued()[0].url)

    def testGetLinksNewsletter(self):
        n = Newsletter("Newsletter 1", "Some text")
        n.number = 1
        n.stored = datetime.fromisoformat("2020-03-07 13:00")
        n.updated = datetime.fromisoformat("2020-03-07 13:00")
        n.sent = True
        n.sentdate = datetime.fromisoformat("2020-03-07 13:00")
        n.slugify()
        newsletter_repo.save(n)
        link = Link(url="http://foo.com/toread1", type=links_repo.TOREAD, newsletter=n.key())

        self.assertEqual(newsletter_repo.get(link.newsletter).to_dict(), n.to_dict())


class SettingTestCase(DatabaseTestCase):
    def testSetting(self):
        settings_repo.set("k1", "v1")
        retval = Database.db.collection(settings_repo.collection).document("k1").get()
        self.assertTrue(retval.exists)
        self.assertEqual({
            "name": "k1",
            "value": "v1"
        }, retval.to_dict())

        self.assertEqual("v1", settings_repo.get("k1"))

    def testDefaultValue(self):
        retval = Database.db.collection(settings_repo.collection).document("k1").get()
        self.assertFalse(retval.exists)

        self.assertEqual("NOT SET", settings_repo.get("k1"))
        retval = Database.db.collection(settings_repo.collection).document("k1").get()
        self.assertTrue(retval.exists)
        self.assertEqual({
            "name": "k1",
            "value": "NOT SET"
        }, retval.to_dict())
