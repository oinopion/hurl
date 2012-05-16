Django has nice routing, but it's too low level. Regexps are powerful, 
but but have cryptic syntax. This library strives to make writing DRY 
urls a breeze.

Consider a standard urls.py:

    urlpatterns = patterns('blog.entries.views',
        url(r'^entries/$', 'recent_entries', name='entries_recent_entries'),
        url(r'^entries/(?<entry_slug>[\w-]+)/$', 'show_entry', name='entries_show_entry'),
        url(r'^entries/(?<entry_slug>[\w-]+)/delete/$', 'delete_entry', name='entries_delete_entry'),
    )

It has many issues:

  - you need to remember about the '^' and the '$'
  - you repeat the base url 'entries'
  - you repeat the entry_slug url
  - you need to remember arcane named group syntax
  - you repeat the [\w-]+ group
  - you associate name with urls conf

Better way of writing urls would be:

    urlpatterns = patterns('blog.entries.views', 
        url('entries', 'recent_entries', [
            url(':entry_slug', 'show_entry', [
                url('delete', 'delete_entry')
                url('edit', 'edit_entry')
            ]),
        ])
    )

    urlpatterns = patterns('blog.entries.views', 
        url('entries', {
            '': 'recent_entries',
            ':entry_slug': {
                '': 'show_entry',
                'delete': 'delete_entry',
                'edit': 'edit_entry'
            }
        })
    )

It conveys url structure more clearly
