Django has nice routing, but it's too low level. Regexps are powerful, 
but but have cryptic syntax. This library strives to make writing DRY 
urls a breeze.

Consider a standard urls.py:

    urlpatterns = patterns('blog.entries.views',
        url(r'^entries/$', 'recent_entries', name='entries_recent_entries'),
        url(r'^entries/(?P<entry_slug>[\w-]+)/$', 'show_entry', name='entries_show_entry'),
        url(r'^entries/(?P<entry_slug>[\w-]+)/new/$', 'new_entry', name='entries_new_entry'),
        url(r'^entries/(?P<entry_slug>[\w-]+)/edit/$', 'edit_entry', name='entries_edit_entry'),
        url(r'^entries/(?P<entry_slug>[\w-]+)/delete/$', 'delete_entry', name='entries_delete_entry'),
        url(r'^entries/(?P<entry_slug>[\w-]+)/comments/$', 'comments_list', name='entries_comments_list'),
        url(r'^entries/(?P<entry_slug>[\w-]+)/comments/(\d+)/$', 'comment_details', name='entries_comment_detail'),
    )

It has many issues:

  - you need to remember about the '^' and the '$'
  - you repeat the base url 'entries'
  - you repeat the entry_slug url
  - you need to remember arcane named group syntax
  - you repeat the [\w-]+ group
  - you associate name with urls conf

Better way of writing urls would be:

    urlpatterns = hurl.patterns('blog.entries.views', {
        '': 'recent_entries',
        '<entry_slug:str>': {
            '': 'show_entry',
            'delete': 'delete_entry',
            'edit': 'delete_entry',
            'new': 'delete_entry',
            'comments': 'comments_list',
            'comments/<:int>': 'comments_list',
        }),
    )

It conveys url structure more clearly

Happy URLs

# original:
urlpatterns = patterns('',
    (r'^articles/2003/$', 'news.views.special_case_2003', {}, 'news_special_case_2003'),
    (r'^articles/(?P<year>\d{4})/$', 'news.views.year_archive'),
    (r'^articles/(?P<year>\d{4})/(?P<month>\d{2})/$', 'news.views.month_archive'),
    (r'^articles/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', 'news.views.article_detail'),
)

# hurled:
hurl = Hurl()
hurl.matchers['year'] = r'\d{4}'
hurl.matchers['month'] = r'\d{2}'
hurl.matchers['month2'] = r'\d{1}'
hurl.matchers['day'] = r'\d{2}'

urlpatterns = hurl.patterns('', 'articles', {
    '2003': 'news.views.special_case_2003',
    '<year>': 'news.views.year_archive',
    '<year>/<month>': 'news.views.month_archive',
    '<year>/<month>/<day>': 'news.views.article_detail',
})





ssl = get_satchmo_setting('SSL', default_value=False)

urlpatterns = patterns('payment.views',
     (r'^$', 'contact.contact_info_view', {'SSL': ssl}, 'satchmo_checkout-step1'),
     (r'^success/$', 'checkout.success', {'SSL' : ssl}, 'satchmo_checkout-success'),
     (r'custom/charge/(?P<orderitem_id>\d+)/$', 'balance.charge_remaining', {}, 'satchmo_charge_remaining'),
     (r'custom/charge/$', 'balance.charge_remaining_post', {}, 'satchmo_charge_remaining_post'),
     (r'^balance/(?P<order_id>\d+)/$', 'balance.balance_remaining_order', {'SSL' : ssl}, 'satchmo_balance_remaining_order'),
     (r'^balance/$', 'balance.balance_remaining', {'SSL' : ssl}, 'satchmo_balance_remaining'),
     (r'^cron/$', 'cron.cron_rebill', {}, 'satchmo_cron_rebill'),
     (r'^mustlogin/$', 'contact.authentication_required', {'SSL' : ssl}, 'satchmo_checkout_auth_required'),
)

hurl.matchers['custom_charge'] = r'custom/charge/(?P<orderitem_id>\d+)'
hurl.name_prefix = 'satchmo'
hurl.default_data = {'SSL': ssl}

urlpatterns = hurl.patterns('payment.views', {
    '': ('contact.contact_info_view', 'checkout-step1'),
    'success': ('checkout.success', 'checkout-success'),
    r'<!custom/charge/(?P<orderitem_id>\d+)>': (balance.charge_remaining', 'charge_remaining', {}),
    'balance': {
        '': ('balance.balance_remaining', 'balance_remaining'),
        '<order_id:int>': ('balance.balance_remaining_order', 'balance_remaining_order')
    },
    'cron': ('cron.cron_rebill', 'cron_rebill', {}),
    'mustlogin': ('contact.authentication_required', 'checkout_auth_required'),
})

urlpatterns = patterns('blog.entries.views',
    url(r'^$', 'recent_entries', name='entries_recent_entries'),
    url(r'^(?P<entry_slug>[\w-]+)/$', 'show_entry', name='entries_show_entry'),
    url(r'^(?P<entry_slug>[\w-]+)/delete/$', 'delete_entry', name='entries_delete_entry'),
    url(r'^(?P<entry_slug>[\w-]+)/new/$', 'new_entry', name='entries_delete_entry'),
    url(r'^(?P<entry_slug>[\w-]+)/comments/$', include('blog.comments.urls'))
)

urlpatterns = hurl.patterns('blog.entries.views', {
    '<entry_slug:str>': {
        '': 'show',
        'delete': 'delete',
        'new': 'new',
        'comments': include('blog.comments.urls'),
        'dupa': ('dupa_view', 'dupa_name', {}),
    }
})



