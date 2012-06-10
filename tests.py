from django.utils import unittest
from django.conf.urls import include, patterns
from django.core.exceptions import ImproperlyConfigured

import hurl

class BasicPatternsTest(unittest.TestCase):
    def test_simple_string(self):
        h = hurl.Hurl()
        result = h.urls({
            '2003': '2003_view',
        })
        expected = (
            (r'^2003/$', '2003_view', None, '2003_view'),
        )
        self.assertSequenceEqual(result, expected)

    def test_with_callable(self):
        def some_view(req):
            return ''
        h = hurl.Hurl()
        result = h.urls({
            '2003': some_view,
        })
        expected = (
            (r'^2003/$', some_view, None, 'some_view'),
        )
        self.assertSequenceEqual(result, expected)

    def test_simple_named_parameter(self):
        h = hurl.Hurl()
        result = h.urls({
            '<id:int>': 'news.views.details',
        })
        expected = (
            (r'^(?P<id>\d+)/$', 'news.views.details', None, 'details'),
        )
        self.assertSequenceEqual(result, expected)

    def test_two_named_parameters(self):
        h = hurl.Hurl()
        result = h.urls({
            'articles' : {
                '<id:int>/<id2:int>': 'news.views.details',
            }
        })
        expected = (
            (r'^articles/(?P<id>\d+)/(?P<id2>\d+)/$', 'news.views.details', None, 'details'),
        )
        self.assertSequenceEqual(result, expected)

    def test_tree_urls(self):
        self.maxDiff = None
        h = hurl.Hurl()
        result = h.urls({
            'articles' : {
                '<id:int>/<id2:int>': 'news.views.details',
                'text/author' : {
                    '<author_id:int>' : 'news.views.author_details',
                    'archive/<author_id:int>' : 'news.views.archive',
                }
            }
        })
        expected = (
            (r'^articles/(?P<id>\d+)/(?P<id2>\d+)/$', 'news.views.details', None, 'details'),
            (r'^articles/text/author/(?P<author_id>\d+)/$', 'news.views.author_details', None, 'author_details'),
            (r'^articles/text/author/archive/(?P<author_id>\d+)/$', 'news.views.archive', None, 'archive'),
        )
        self.assertItemsEqual(result, expected)

    def test_slug_named_type(self):
        h = hurl.Hurl()
        result = h.urls({
            '<id:slug>': 'news.views.details',
        })
        expected = (
            (r'^(?P<id>[\w-]+)/$', 'news.views.details', None, 'details'),
        )
        self.assertSequenceEqual(result, expected)

    def test_custom_named_type(self):
        h = hurl.Hurl()
        h.matchers['year'] = r'\d{4}'
        result = h.urls({
            '<year:year>': 'news.views.details',
        })
        expected = (
            (r'^(?P<year>\d{4})/$', 'news.views.details', None, 'details'),
        )
        self.assertSequenceEqual(result, expected)

    def test_custom_guessed_named_type(self):
        h = hurl.Hurl()
        h.matchers['year'] = r'\d{4}'
        result = h.urls({
            '<year>': 'news.views.details',
        })
        expected = (
            (r'^(?P<year>\d{4})/$', 'news.views.details', None, 'details'),
        )
        self.assertSequenceEqual(result, expected)

    def test_default_type_is_slug(self):
        h = hurl.Hurl()
        result = h.urls({
            '<year>': 'news.views.details',
        })
        expected = (
            (r'^(?P<year>[\w-]+)/$', 'news.views.details', None, 'details'),
        )
        self.assertSequenceEqual(result, expected)

    def test_setting_custom_default_type(self):
        h = hurl.Hurl()
        h.default_matcher = 'int'
        result = h.urls({
            '<year>': 'news.views.details',
        })
        expected = (
            (r'^(?P<year>\d+)/$', 'news.views.details', None, 'details'),
        )
        self.assertSequenceEqual(result, expected)



    def test_empty_url(self):
        h = hurl.Hurl()
        result = h.urls({
            '': 'details',
        })
        expected = (
            (r'^$', 'details', None, 'details'),
        )
        self.assertSequenceEqual(result, expected)

    def test_empty_nested_url(self):
        h = hurl.Hurl()
        result = h.urls({
            'bla': {
                '': 'details',
            }
        })
        expected = (
            (r'^bla/$', 'details', None, 'details'),
        )
        self.assertSequenceEqual(result, expected)

    def test_no_name_only_type(self):
        h = hurl.Hurl()
        result = h.urls({
            '<:int>': 'details',
        })
        expected = (
            (r'^(\d+)/$', 'details', None, 'details'),
        )
        self.assertSequenceEqual(result, expected)


    def test_name_prefix(self):
        h = hurl.Hurl(name_prefix='news')
        result = h.urls({
            '<id:int>': 'news.views.details',
            })
        expected = (
            (r'^(?P<id>\d+)/$', 'news.views.details', None, 'news_details'),
            )
        self.assertSequenceEqual(result, expected)

    def test_include(self):
        h = hurl.Hurl()
        urlpatterns = h.patterns('', {
            '<id:int>': 'news.views.details',
        })
        result = h.urls({
            '<id:int>': {
                '': 'news.views.details',
                'comments': h.include(urlpatterns)
            }
        })
        expected = (
            (r'^(?P<id>\d+)/$', 'news.views.details', None, 'details'),
            (r'^(?P<id>\d+)/comments/$', (urlpatterns, None, None), None, None),
        )
        self.assertEqual(result[0], expected[0])
        self.assertEqual(result[1][0], expected[1][0])
        self.assertEqual(result[1][2], expected[1][2])
        self.assertEqual(result[1][3], expected[1][3])
        self.assertEqual(result[1][1][0][0].__dict__, expected[1][1][0][0].__dict__)

    def test_regexurlpatter_returned(self):
        h = hurl.Hurl()
        urlpatterns = h.patterns('', {
            '<id:int>': 'news.views.details'
        })
        expected = patterns('',
            (r'^(?P<id>[0-9]+)/', 'news.views.details', None, 'news_details')
        )
        self.assertTrue(urlpatterns, expected)


#class TestParser(unittest.TestCase):
class TestParser():

    # expression := STRING
    def test_simple_string_is_expression(self):
        parser = hurl.Parser()
        input_text = "entries"
        expected_result = [hurl.StaticPart('entries')]
        result = parser.parse(input_text)
        self.assertEquals(result, expected_result)

    # parameter := < NAME_TYPE >
    def test_name_type_parameter(self):
        parser = hurl.Parser()
        input_text = "<year>"
        expected_result = [hurl.PatternPart(name='year')]
        result = parser.parse(input_text)
        self.assertEquals(result, expected_result)

    # parameter := < NAME : TYPE >
    def test_full_name_type_parameter(self):
        parser = hurl.Parser()
        input_text = "<id:int>"
        expected_result = [hurl.PatternPart(name='id', type='int')]
        result = parser.parse(input_text)
        self.assertEquals(result, expected_result)

    # parameter := < : ONLY_TYPE >
    def test_only_type_parameter(self):
        parser = hurl.Parser()
        input_text = "<:int>"
        expected_result = [hurl.PatternPart(type='int')]
        result = parser.parse(input_text)
        self.assertEquals(result, expected_result)

    def test_no_whitespace_in_parameter(self):
        parser = hurl.Parser()
        input_text = "< : int   >"
        expected_result = [hurl.PatternPart(type='int')]
        result = parser.parse(input_text)
        self.assertEquals(result, expected_result)

        input_text = "  <  id :   int    >   "
        expected_result = [hurl.PatternPart(name='id', type='int')]
        result = parser.parse(input_text)
        self.assertEquals(result, expected_result)

    # expression := STRING / STRING
    def test_string_slash_pattern(self):
        parser = hurl.Parser()
        input_text = "blog/authors"
        expected_result = [hurl.StaticPart('blog'), hurl.StaticPart('authors')]
        result = parser.parse(input_text)
        self.assertEquals(result, expected_result)

    # expression := STRING / STRING / STRING / STRING
    def test_multiple_slash_strings(self):
        parser = hurl.Parser()
        input_text = "blog/author/john/smith"
        expected_result = [hurl.StaticPart('blog'),
                           hurl.StaticPart('author'),
                           hurl.StaticPart('john'),
                           hurl.StaticPart('smith')]
        result = parser.parse(input_text)
        self.assertEquals(result, expected_result)

    # expression := STRING / < NAME >
    def test_string_slash_parameter(self):
        parser = hurl.Parser()
        input_text = "blog/<day>"
        expected_result = [hurl.StaticPart('blog'), hurl.PatternPart(name='day')]
        result = parser.parse(input_text)
        self.assertEquals(result, expected_result)

    # expression := STRING / < NAME : TYPE >
    def test_string_slash_parameter_type(self):
        parser = hurl.Parser()
        input_text = "blog/<id:int>"
        expected_result = [hurl.StaticPart('blog'), hurl.PatternPart(name='id', type='int')]
        result = parser.parse(input_text)
        self.assertEquals(result, expected_result)

    # expression := STRING / < : ONLY_TYPE >
    def test_string_slash_parameter_only_type(self):
        parser = hurl.Parser()
        input_text = "blog/<:int>"
        expected_result = [hurl.StaticPart('blog'), hurl.PatternPart(type='int')]
        result = parser.parse(input_text)
        self.assertEquals(result, expected_result)

    # expression := < NAME > / STRING
    def test_string_slash_parameter_only_type(self):
        parser = hurl.Parser()
        input_text = "<author>/blog"
        expected_result = [hurl.PatternPart(name='author'), hurl.StaticPart('blog')]
        result = parser.parse(input_text)
        self.assertEquals(result, expected_result)

    # expression := < NAME : TYPE > / STRING
    def test_string_slash_parameter_name_type(self):
        parser = hurl.Parser()
        input_text = "<id:int>/blog/"
        expected_result = [hurl.PatternPart(name='id', type='int'), hurl.StaticPart('blog')]
        result = parser.parse(input_text)
        self.assertEquals(result, expected_result)

    # expression := < : ONLY_TYPE > / STRING
    def test_string_slash_parameter_only_type(self):
        parser = hurl.Parser()
        input_text = "<:int>/blog/"
        expected_result = [hurl.PatternPart(type='int'), hurl.StaticPart('blog')]
        result = parser.parse(input_text)
        self.assertEquals(result, expected_result)

    # error handling
    def test_invalid_number_of_gt(self):
        parser = hurl.Parser()
        input_text = "<:int/blog/"
        self.assertRaises(ImproperlyConfigured, parser.parse, input_text)

    def test_invalid_number_of_lt(self):
        parser = hurl.Parser()
        input_text = "><:int/blog/"
        self.assertRaises(ImproperlyConfigured, parser.parse, input_text)

        parser = hurl.Parser()
        input_text = "<asdf:/asdfas>"
        self.assertRaises(ImproperlyConfigured, parser.parse, input_text)

        input_text = "<:int/>blog/"
        self.assertRaises(ImproperlyConfigured, parser.parse, input_text)

        input_text = "int/blog>/"
        self.assertRaises(ImproperlyConfigured, parser.parse, input_text)

        input_text = "<int/blog/"
        self.assertRaises(ImproperlyConfigured, parser.parse, input_text)

    def test_no_spaces_in_parameter_name_possible(self):
        parser = hurl.Parser()
        input_text = "<year day>"
        self.assertRaises(ImproperlyConfigured, parser.parse, input_text)

    def test_no_spaces_in_type_name_possible(self):
        parser = hurl.Parser()
        input_text = "<:year day>"
        self.assertRaises(ImproperlyConfigured, parser.parse, input_text)

    def test_cannot_have_more_than_one_colon(self):
        parser = hurl.Parser()
        input_text = "<:year:day>"
        self.assertRaises(ImproperlyConfigured, parser.parse, input_text)

if __name__ == '__main__':
    unittest.main()
