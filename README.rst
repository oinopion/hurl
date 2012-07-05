Django Happy Urls
=================

This is early work. Expect very weird errors.
Comments/feedback is very welcome, use issues or twitter: https://twitter.com/oinopion 

.. image:: https://secure.travis-ci.org/oinopion/hurl.png

Django has nice routing, but it's too low level. Regexps are powerful,
but have cryptic syntax. This library strives to make writing DRY
urls a breeze.

Consider a standard urls.py::

    urlpatterns = patterns('blog.entries.views',
        url(r'^$', 'recent_entries', name='entries_recent_entries'),
        url(r'^new/$', 'new_entry', name='entries_new_entry'),
        url(r'^(?P<entry_slug>[\w-]+)/$', 'show_entry', name='entries_show_entry'),
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

    urlpatterns = hurl.patterns('blog.entries.views', [
        ('', 'recent_entries'),
        ('new', 'new_entry'),
        ('<entry_slug>', [
            ('', 'show_entry'),
            ('edit', 'edit_entry'),
            ('delete', 'delete_entry'),
            ('comments', 'comments_list'),
            ('comments/<:int>', 'comment_detail'),
        ]),
    ])

It conveys url structure more clearly, is much more readable and
avoids repetition. If your views don't rely on order, you can also use
dictionary like this::

    urlpatterns = hurl.patterns('blog.entries.views', {
        'show': 'show_entry',
        'edit': 'edit_entry',
        'delete': 'delete_entry',
    })


How to use it
-------------

patterns (prefix, url_conf)

    * prefix is same as in django.conf.url.patterns
    * url_conf is either a dictionary or a list of 2-tuples
        The key (in dict) or first element (tuple) is a url fragment,
        value/second element can be one of: another url_conf, a string, an instance
        of ViewSpec.

        {
            'show': 'blog.views.show_entry',
        }
        is equivalent to
        [
            ('show', 'blog.views.show_entry'),
        ]

        URL conf creates a tree of url fragments and generates a list
        by joining each fragment with the "/"::

            {
                'entries': {
                    'edit': 'edit_entry',
                    'delete': 'delete_entry',
                }
            }

        This will generate urls::

            (r'^entries/edit/$', 'edit_entry')
            (r'^entries/delete/$', 'delete_entry')


        Url fragment may include multiple parameters in format::

       '<parameter_name:parameter_type>'

       parameter_name can be any python identifier
       parameter_type must be one of default or defined matchers

       If you have parameter_type same as parameter_name, you can skip
       duplication and use shorter form::
            '<int:int>' -> '<int>'


        If you want to use default matcher also use shortcut::
            '<blog_slug:slug>' -> '<blog_slug>'

        If you don't want to define parameter name, leave it empty::

            '<:int>' # will generate r'(\d+)'



Default Matchers
----------------

    :slug:

        r'[\w-]+'
        This is the default matcher.

    :int:

        r'\d+'

    :str:

        r'[^/]+'

Custom Matchers
---------------

You can define your own matchers. Just instantiate Hurl and set::

    import hurl
    h = hurl.Hurl()
    h.matchers['year'] = r'\d{4}'

    urlpatterns = h.patterns('', {'<year>': 'year_archive'})

.. note::

    When defining custom matchers use the 'patterns' method of your instance,
    rather than function provided by module.

Names generation
----------------

Hurl will automatically generate view names for you. When provided with
view as string ('blog.views.show_entry') it will take last part after the dot.
When provided with function it will take the func_name of it::

    def some_view(req):
        pass

    urlpatterns = hurl.patterns('', {
        'show': 'blog.views.show_entry', # generates 'show_entry' name
        'some': some_view, # generates 'some_view' name
    })

You can also want to change the name use the 'v' function::

    import hurl
    urlpatterns = hurl.patterns('', {
        'show': hurl.v('show_view', name='show'),
    })

Includes
--------

If you want to include some other urlpatterns, use the `include` method::

    import hurl
    urlpatterns = hurl.patterns('', {
        'shop': hurl.include('shop.urls'),
        'blog': hurl.include('blog.urls'),
    })


Mixing with pure Django urls
----------------------------

Hurl doesn't do anything special, it just generates plain old Django urls.
You can easily mix two APIs::

    from django.conf.urls import url, include, patterns
    import hurl

    urlpatterns = patterns('', # plain Django
        url(r'^hello/$
    )


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

