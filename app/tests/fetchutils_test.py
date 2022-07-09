import unittest
from fetchutils import notion_richtext_to_markdown


class NotionToMDTestCase(unittest.TestCase):
    def test_basic_paragraphs(self):
        expected = """This is a paragraph. 

This is a second paragraph. 

This is a third paragraph. """
        input = [{
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "This is a paragraph.",
            "text": {
                "content": "This is a paragraph.",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "This is a second paragraph.",
            "text": {
                "content": "This is a second paragraph.",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "This is a third paragraph.",
            "text": {
                "content": "This is a third paragraph.",
                "link": None
            },
            "type": "text"
        }]

        self.assertEqual(expected, notion_richtext_to_markdown(input))

    def test_bold_formating(self):
        expected = """This is **bold** in a paragraph. 

This is a second paragraph. """
        input = [{
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "This is ",
            "text": {
                "content": "This is ",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": True,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "bold",
            "text": {
                "content": "bold",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": " in a paragraph.",
            "text": {
                "content": " in a paragraph.",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "This is a second paragraph.",
            "text": {
                "content": "This is a second paragraph.",
                "link": None
            },
            "type": "text"
        }]

        self.assertEqual(expected, notion_richtext_to_markdown(input))

    def test_strikethrough_formating(self):
        expected = """This is ~~strikethrough~~ in a paragraph. 

This is a second paragraph. """
        input = [{
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "This is ",
            "text": {
                "content": "This is ",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": True,
                "underline": False
            },
            "href": None,
            "plain_text": "strikethrough",
            "text": {
                "content": "strikethrough",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": " in a paragraph.",
            "text": {
                "content": " in a paragraph.",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "This is a second paragraph.",
            "text": {
                "content": "This is a second paragraph.",
                "link": None
            },
            "type": "text"
        }]

        self.assertEqual(expected, notion_richtext_to_markdown(input))

    def test_code_formating(self):
        expected = """This is `code` in a paragraph. 

This is a second paragraph. """
        input = [{
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "This is ",
            "text": {
                "content": "This is ",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": True,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "code",
            "text": {
                "content": "code",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": " in a paragraph.",
            "text": {
                "content": " in a paragraph.",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "This is a second paragraph.",
            "text": {
                "content": "This is a second paragraph.",
                "link": None
            },
            "type": "text"
        }]

        self.assertEqual(expected, notion_richtext_to_markdown(input))

    def test_italic_formating(self):
        expected = """This is _italic_ in a paragraph. 

This is a second paragraph. """
        input = [{
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "This is ",
            "text": {
                "content": "This is ",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": True,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "italic",
            "text": {
                "content": "italic",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": " in a paragraph.",
            "text": {
                "content": " in a paragraph.",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "This is a second paragraph.",
            "text": {
                "content": "This is a second paragraph.",
                "link": None
            },
            "type": "text"
        }]

        self.assertEqual(expected, notion_richtext_to_markdown(input))

    def test_complex_formating(self):
        expected = """This is **_bold italic_** **along with** **`bold code`** in a paragraph. 

This is a second paragraph. """
        input = [{
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "This is ",
            "text": {
                "content": "This is ",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": True,
                "code": False,
                "color": "default",
                "italic": True,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "bold italic",
            "text": {
                "content": "bold italic",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": True,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "along with",
            "text": {
                "content": "along with",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": True,
                "code": True,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "bold code",
            "text": {
                "content": "bold code",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": " in a paragraph.",
            "text": {
                "content": " in a paragraph.",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "This is a second paragraph.",
            "text": {
                "content": "This is a second paragraph.",
                "link": None
            },
            "type": "text"
        }]

        self.assertEqual(expected, notion_richtext_to_markdown(input))

    def test_links_in_paragraphs(self):
        expected = """This is a paragraph with a [link](http://www.example.com) in the middle. 

This is a second paragraph. 

This is a third paragraph. """
        input = [{
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "This is a paragraph with a ",
            "text": {
                "content": "This is a paragraph with a ",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": "http://www.example.com",
            "plain_text": "link",
            "text": {
                "content": "link",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "in the middle.",
            "text": {
                "content": "in the middle.",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "This is a second paragraph.",
            "text": {
                "content": "This is a second paragraph.",
                "link": None
            },
            "type": "text"
        }, {
            "annotations": {
                "bold": False,
                "code": False,
                "color": "default",
                "italic": False,
                "strikethrough": False,
                "underline": False
            },
            "href": None,
            "plain_text": "This is a third paragraph.",
            "text": {
                "content": "This is a third paragraph.",
                "link": None
            },
            "type": "text"
        }]

        self.assertEqual(expected, notion_richtext_to_markdown(input))
