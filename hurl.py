class Hurl(object):
    default_matcher = 'slug'
    DEFAULT_MATCHERS = {
        'int': r'\d+',
        'slug': r'[\w-]+'
    }

    def __init__(self, name_prefix=''):
        self.name_prefix = name_prefix
        self.matchers = dict(self.DEFAULT_MATCHERS)

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
            if type(view) == dict:
                re_list = self.patterns_recursive(view)
                for p, v in re_list:
                    urls.append((re_str + '/' + p, v))
            else:
                urls.append((re_str, view))
        return urls

    def add_prefix_suffix(self, urls):
        formatted_urls = []
        for url, view in urls:
            formatted_urls.append(('^{url}/$'.format(url=url), view))
        return formatted_urls

    def add_views_prefix(self, prefix, urls):
        new_urls = []
        for url, view in urls:
            full_view_name = '.'.join((prefix, view))
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
        return '{}'.format(''.join(parts))

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
            name = view.split('.')[-1]
            if self.name_prefix:
                name = '{prefix}_{name}'.format(prefix=self.name_prefix, name=name)
            new_urls.append((url, view, {}, name))
        return new_urls
