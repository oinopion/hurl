Django Happy Urls
=================

This is early work. Expect very weird errors.
Comments/feedback is very welcome, use issues or twitter: https://twitter.com/oinopion 

Django has nice routing, but it's too low level. Regexps are powerful,
but but have cryptic syntax. This library strives to make writing DRY 
urls a breeze.

Consider a standard urls.py::

    urlpatterns = patterns('blog.entries.views',
        url(r'^$', 'recent_entries', name='entries_recent_entries'),
        url(r'^(?P<entry_slug>[\w-]+)/$', 'show_entry', name='entries_show_entry'),
        url(r'^(?P<entry_slug>[\w-]+)/new/$', 'new_entry', name='entries_new_entry'),
        url(r'^(?P<entry_slug>[\w-]+)/edit/$', 'edit_entry', name='entries_edit_entry'),
        url(r'^(?P<entry_slug>[\w-]+)/delete/$', 'delete_entry', name='entries_delete_entry'),
        url(r'^(?P<entry_slug>[\w-]+)/comments/$', 'comments_list', name='entries_comments_list'),
        url(r'^(?P<entry_slug>[\w-]+)/comments/(\d+)/$', 'comment_details', name='entries_comment_detail'),
    )

It has many issues:

- you need to remember about the '^' and the '$'
- you repeat the entry_slug url
- you need to remember arcane named group syntax
- you repeat the [\\w-]+ group
- you associate name with urls conf

Better way of writing urls would be::

    urlpatterns = hurl.patterns('blog.entries.views', {
        '': 'recent_entries',
        '<entry_slug:str>': {
            '': 'show_entry',
            'new': 'new_entry',
            'edit': 'edit_entry',
            'delete': 'delete_entry',
            'comments': 'comments_list',
            'comments/<:int>': 'comment_detail',
        }),
    )

It conveys url structure more clearly, is much more readable and
avoids repetition.

More examples
-------------

Django tutorial::

    # original:
    urlpatterns = patterns('',
        (r'^articles/2003/$', 'news.views.special_case_2003', {}, 'news_special_case_2003'),
        (r'^articles/(?P<year>\d{4})/$', 'news.views.year_archive', {}, 'news_year_archive'),
        (r'^articles/(?P<year>\d{4})/(?P<month>\d{2})/$', 'news.views.month_archive', {}, 'news_month_archive'),
        (r'^articles/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', 'news.views.article_detail', {}, 'news_article_detail'),
    )

    # hurled:
    hurl = Hurl(name_prefix='news')
    hurl.matchers['year'] = r'\d{4}'
    hurl.matchers['month'] = r'\d{2}'
    hurl.matchers['day'] = r'\d{2}'

    urlpatterns = hurl.patterns('news.views', {
        'articles': {
            '2003': 'special_case_2003',
            '<year>': 'year_archive',
            '<year>/<month>': 'month_archive',
            '<year>/<month>/<day>': 'article_detail',
        }
    })

