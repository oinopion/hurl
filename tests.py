import unittest
import hurl

class BasicPatterns(unittest.TestCase):
    def test_simple_string(self):
        h = hurl.Hurl()
        result = h.patterns('', {
            '2003': '2003_view',
        })
        expected = (
            (r'^2003/$', '2003_view'),
        )
        self.assertSequenceEqual(result, expected)

    def test_simple_named_parameter(self):
        h = hurl.Hurl()
        result = h.patterns('', {
            '<id:int>': 'news.views.details',
        })
        expected = (
            (r'^(?P<id>\d+)/$', 'news.views.details'),
        )
        self.assertSequenceEqual(result, expected)

    def test_two_named_parameters(self):
        h = hurl.Hurl()
        result = h.patterns('', {
            'articles' : {
                '<id:int>/<id2:int>': 'news.views.details',
            }
        })
        expected = (
            (r'^articles/(?P<id>\d+)/(?P<id2>\d+)/$', 'news.views.details'),
        )
        self.assertSequenceEqual(result, expected)

    def test_tree_urls(self):
            h = hurl.Hurl()
            result = h.patterns('', {
                'articles' : {
                    '<id:int>/<id2:int>': 'news.views.details',
                    'text/author' : {
                        '<author_id:int>' : 'news.views.author_details',
                        'archive/<author_id:int>' : 'news.views.archive',
                    }
                }
            })
            expected = (
                (r'^articles/(?P<id>\d+)/(?P<id2>\d+)/$', 'news.views.details'),
                (r'^articles/text/author/(?P<author_id>\d+)/$', 'news.views.author_details'),
                (r'^articles/text/author/archive/(?P<author_id>\d+)/$', 'news.views.archive'),
            )
            self.assertItemsEqual(result, expected)

    def test_slug_named_type(self):
        h = hurl.Hurl()
        result = h.patterns('', {
            '<id:slug>': 'news.views.details',
        })
        expected = (
            (r'^(?P<id>[\w-]+)/$', 'news.views.details'),
        )
        self.assertSequenceEqual(result, expected)
