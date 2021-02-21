import unittest

from google.cloud import firestore
from mockfirestore import MockFirestore
from models import Newsletter, Link, Database, Settings
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
        n.save()
        
        n = Newsletter("Newsletter 2", "Some other text")
        n.number = 2
        n.stored = datetime.fromisoformat("2020-03-08 13:00")
        n.updated = datetime.fromisoformat("2020-03-08 13:00")
        n.sent = True
        n.sentdate = datetime.fromisoformat("2020-03-08 13:00")
        n.slugify()
        n.save()

        n = Newsletter("Newsletter 3", "Draft newsletter")
        n.number = 3
        n.stored = datetime.fromisoformat("2020-03-09 13:00")
        n.updated = datetime.fromisoformat("2020-03-09 13:00")
        n.slugify()
        n.save()

        
    def testNewsletter(self):
        actual = Newsletter('Kids in America', 'some text')
        actual.number = 777
        actual.save()

        self.assertEquals("777", actual.key())

        retval = Database.db.collection(Newsletter.collection).document("777").get()
        self.assertTrue(retval.exists)
        self.assertDictContainsSubset({
            "number": 777,
            "title": 'Kids in America',
            "body": "some text",
            "slug": None,
        }, retval.to_dict())

    def testNewsletterSlugs(self):
        actual = Newsletter("Kids in America","some text")
        self.assertEqual("Kids in America", actual.title)

        self.assertEqual(None, actual.slug)
        self.assertEqual("kids-in-america", actual.slugify())
        self.assertEqual("kids-in-america", actual.slug)

    def testQueries(self):
        self.createTestData()

        self.assertEquals(3, len(list(Newsletter.list())))
        newsletters = [Newsletter.from_dict(d.to_dict()) for d in Newsletter.list_published()]
        self.assertEquals(2, len(newsletters))
        self.assertEquals(2, newsletters[0].number)
        self.assertEquals(1, newsletters[1].number)

        self.assertEquals(3, Newsletter.most_recent().number)
        self.assertEquals(2, Newsletter.most_recent_published().number)

    def testGetByNumber(self):
        self.createTestData()
        n = Newsletter.by_number(2)
        self.assertEquals("Newsletter 2", n.title)
        n = Newsletter.by_slug("newsletter-1")
        self.assertEquals("Newsletter 1", n.title)
        n = Newsletter.get("1")
        self.assertEquals("Newsletter 1", n.title)


class LinkTestCase(DatabaseTestCase):
    def testLink(self):
        actual = Link(url="http://foo.com/something", type=Link.TOREAD)
        id = actual.key
        actual.save()
        retval = Database.db.collection(Link.collection).document(id).get()
        self.assertTrue(retval.exists)
        self.assertDictContainsSubset({
            "key": id,
            "url": "http://foo.com/something",
            "type": Link.TOREAD,
        }, retval.to_dict())

        ret = Link.get(id)
        self.assertEquals("http://foo.com/something", ret.url)
        self.assertEquals(id, ret.key)

    def testLinkLifecycle(self):
        self.assertEqual(0, len(list(Link.toread())))
        self.assertEqual(0, len(list(Link.drafts())))
        self.assertEqual(0, len(list(Link.queued())))

        actual = Link(url="http://foo.com/thing", type=Link.TOREAD)
        actual.save()

        self.assertEqual(1, len(list(Link.toread())))
        self.assertEqual(0, len(list(Link.drafts())))
        self.assertEqual(0, len(list(Link.queued())))

        actual.type = Link.DRAFT
        actual.save()

        self.assertEqual(0, len(list(Link.toread())))
        self.assertEqual(1, len(list(Link.drafts())))
        self.assertEqual(0, len(list(Link.queued())))

        actual.type = Link.QUEUED
        actual.save()

        self.assertEqual(0, len(list(Link.toread())))
        self.assertEqual(0, len(list(Link.drafts())))
        self.assertEqual(1, len(list(Link.queued())))

        Link.delete(actual.key)

        self.assertEqual(0, len(list(Link.toread())))
        self.assertEqual(0, len(list(Link.drafts())))
        self.assertEqual(0, len(list(Link.queued())))

    def createTestData(self):
        Link(url="http://foo.com/toread1", type=Link.TOREAD).save()
        Link(url="http://foo.com/toread2", type=Link.TOREAD).save()
        Link(url="http://foo.com/draft1", type=Link.DRAFT).save()
        Link(url="http://foo.com/queued1", type=Link.QUEUED).save()
        Link(url="http://foo.com/deleted1", type=Link.DELETED).save()

    def testQueries(self):
        self.createTestData()
        self.assertEquals("http://foo.com/toread2", Link.toread()[0].url)
        self.assertEquals("http://foo.com/toread1", Link.toread()[1].url)
        self.assertEquals("http://foo.com/draft1", Link.drafts()[0].url)
        self.assertEquals("http://foo.com/queued1", Link.queued()[0].url)



class SettingTestCase(DatabaseTestCase):
    def testSetting(self):
        actual = Settings.set("k1", "v1")
        retval = Database.db.collection(Settings.collection).document("k1").get()
        self.assertTrue(retval.exists)
        self.assertEquals({
            "name": "k1",
            "value": "v1"
        }, retval.to_dict())

        self.assertEquals("v1", Settings.get("k1"))

    def testDefaultValue(self):
        retval = Database.db.collection(Settings.collection).document("k1").get()
        self.assertFalse(retval.exists)

        self.assertEquals("NOT SET", Settings.get("k1"))
        retval = Database.db.collection(Settings.collection).document("k1").get()
        self.assertTrue(retval.exists)
        self.assertEquals({
            "name": "k1",
            "value": "NOT SET"
        }, retval.to_dict())
