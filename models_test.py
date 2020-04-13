import unittest

from google.appengine.ext import ndb
from google.appengine.ext import testbed
from models import Newsletter, Link, PlacementLive, PlacementDraft, NewsletterDraft, NewsletterLive


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

class LinkPlacementTestCase(DatabaseTestCase):
    def testLinkLifecycle(self):
        actual = Link(url="http://foo.com/thing", type=Link.TOREAD, title="Some title", quote="some quote", note="some note")
        actual.put()

        placement = PlacementDraft.from_link(actual)
        self.assertEqual("http://foo.com/thing", placement.url)
        self.assertEqual("Some title", placement.title)
        self.assertEqual("some quote", placement.quote)
        self.assertEqual("some note", placement.note)

        newsletter = NewsletterDraft(id = 7, title = "Newsletter", intro = "Welcome to my newsletter")
        newsletter.put()
        newsletter.add_placement(placement)

        self.assertEqual(newsletter.key, placement.newsletter)
        # self.assertEqual(1, placement.order)

        actual2 = Link(url="http://foo.com/thing2", type=Link.TOREAD, title="Some title2", quote="some quote2", note="some note2")
        actual.put()

        placement2 = PlacementDraft.from_link(actual2)
        newsletter.add_placement(placement2)
        self.assertEqual(newsletter.key, placement2.newsletter)
        # self.assertEqual(2, placement2.order)

        self.assertEqual([placement2, placement], newsletter.placements())

        # newsletter.set_order(placement2, 1)
        placement.put()

        self.assertEqual([placement, placement2], newsletter.placements())

        livenewsletter = newsletter.launch()

        liveplacements = livenewsletter.placements()
        self.assertEqual(livenewsletter.__class__, NewsletterLive)
        self.assertEqual(7, livenewsletter.id)
        self.assertEqual("Newsletter", livenewsletter.title)
        self.assertEqual("Welcome to my newsletter", livenewsletter.intro)
        self.assertEqual(2, len(livenewsletter.placements()))
        for p in liveplacements:
            self.assertEqual(PlacementLive, p.__class__)
            self.assertEqual(livenewsletter.key, p.newsletter)

        # Show we can edit and save the draft without touching the live one
        newsletter.title = "New title"
        placement.title = "New draft placement"
        newsletter.put()
        self.assertEqual("New title", newsletter.title)
        self.assertEqual("New draft placement", newsletter.placements()[0].title)
        self.assertEqual("Newsletter", livenewsletter.title)
        self.assertEqual("Some title", livenewsletter.placements()[0].title)

        # RElaunch, overwriting the old one
        livenewsletter2 = newsletter.launch()
        self.assertEqual("New title", livenewsletter2.title)
        self.assertEqual(livenewsletter, livenewsletter2)
        self.assertEqual(2, len(livenewsletter.placements()))
        self.assertEqual("New draft placement", livenewsletter.placements()[0].title)

