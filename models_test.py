import unittest

from google.appengine.ext import ndb
from google.appengine.ext import testbed
from models import Newsletter, Link


class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()


class NewsletterTestCase(DatabaseTestCase):
    def testNewsleterSlugs(self):
        actual = Newsletter(title="Kids in America")
        self.assertEqual(None, actual.slug)
        self.assertEqual("kids-in-america", actual.slugify())
        self.assertEqual("kids-in-america", actual.slug)


class LinkTestCase(DatabaseTestCase):
    def testLinkLifecycle(self):
        actual = Link(url="http://foo.com/thing", type=Link.TOREAD)
        actual.put()

        self.assertEqual(1, len(Link.toread().fetch(2)))
        self.assertEqual(0, len(Link.drafts().fetch(2)))
        self.assertEqual(0, len(Link.queued().fetch(2)))

        actual.type = Link.DRAFT
        actual.put()

        self.assertEqual(0, len(Link.toread().fetch(2)))
        self.assertEqual(1, len(Link.drafts().fetch(2)))
        self.assertEqual(0, len(Link.queued().fetch(2)))

        actual.type = Link.QUEUED
        actual.put()

        self.assertEqual(0, len(Link.toread().fetch(2)))
        self.assertEqual(0, len(Link.drafts().fetch(2)))
        self.assertEqual(1, len(Link.queued().fetch(2)))

        Link.delete(actual.key.urlsafe())

        self.assertEqual(0, len(Link.toread().fetch(2)))
        self.assertEqual(0, len(Link.drafts().fetch(2)))
        self.assertEqual(0, len(Link.queued().fetch(2)))
