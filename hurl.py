from django.core.urlresolvers import RegexURLPattern

class Hurl(object):
    default_matcher = 'slug'
    DEFAULT_MATCHERS = {
        'int': r'\d+',
        'slug': r'[\w-]+'
    }

    def __init__(self, name_prefix=''):
        self.name_prefix = name_prefix
        self.matchers = dict(self.DEFAULT_MATCHERS)

    def urlpatterns(self, prefix, pattern_dict):
        patterns = self.patterns(prefix, pattern_dict)
        urlpatterns = []
        for p in patterns:
            urlpatterns.append(RegexURLPattern(*p))
        return urlpatterns

    def patterns(self, prefix, pattern_dict):
        urls = self.patterns_recursive(pattern_dict)
        urls = self.add_prefix_suffix(urls)
        if prefix:
            urls = self.add_views_prefix(prefix, urls)
        urls = self.add_names(urls)
        return urls

    def patterns_recursive(self, pattern_dict):
        urls = []
        for url, view in pattern_dict.items():
            re_str = self.make_re_str(url)
            if isinstance(view, dict):
                re_list = self.patterns_recursive(view)
                for pattern, view_name in re_list:
                    if pattern == '':
                        urls.append((re_str, view_name))
                    else:
                        urls.append((re_str + '/' + pattern, view_name))
            else:
                urls.append((re_str, view))
        return urls

    def add_prefix_suffix(self, urls):
        formatted_urls = []
        for url, view in urls:
            if url != '':
                url = '^{url}/$'.format(url=url)
            else:
                url = '^$'
            formatted_urls.append((url, view))
        return formatted_urls

    def add_views_prefix(self, prefix, urls):
        new_urls = []
        for url, view in urls:
            if isinstance(view, basestring):
                full_view_name = '.'.join((prefix, view))
            else:
                full_view_name = view
            new_urls.append((url, full_view_name))
        return new_urls

    def make_re_str(self, url):
        parts = []
        s = ''
        for c in url:
            if c == '<':
                parts.append(s)
                s = ''
            elif c == '>':
                parts.append(self.transform(s))
                s = ''
            else:
                s += c
        parts.append(s)
        return '{0}'.format(''.join(parts))

    def transform(self, pattern):
        parts = pattern.split(':')
        if len(parts) == 1:
            name = parts[0]
            type = name
        elif len(parts) == 2:
            name, type = parts
        else:
            raise StandardError('Fix')
        matcher = self.generate_matcher(type)
        if name:
            return r'(?P<{name}>{matcher})'.format(name=name, matcher=matcher)
        else:
            return r'({matcher})'.format(matcher=matcher)


    def generate_matcher(self, type):
        try:
            return self.matchers[type]
        except KeyError:
            return self.matchers[self.default_matcher]

    def add_names(self, urls):
        new_urls = []
        for url, view in urls:
            if isinstance(view, basestring):
                name = view.split('.')[-1]
                if self.name_prefix:
                    name = '{prefix}_{name}'.format(prefix=self.name_prefix, name=name)
                new_urls.append((url, view, {}, name))
            elif callable(view):
                name = getattr(view, 'func_name')
                if name:
                    if self.name_prefix:
                        name = '{prefix}_{name}'.format(prefix=self.name_prefix, name=name)
                    new_urls.append((url, view, {}, name))
                else:
                    new_urls.append((url, view))
            else:
                new_urls.append((url, view))
        return new_urls


def urlpatterns( prefix, pattern_dict):
    h = Hurl()
    return h.urlpatterns(prefix, pattern_dict)

