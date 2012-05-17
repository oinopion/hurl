class Hurl(object):
    DEFAULT_MATCHERS = {
        'int': r'\d+',
        'slug': r'[\w-]+'
    }

    def __init__(self):
        self.matchers = dict(self.DEFAULT_MATCHERS)

    def patterns(self, prefix, pattern_dict):
        urls = self.patterns_recursive(pattern_dict)
        urls = self.add_prefix_suffix(urls)
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
        if 0 < len(parts) < 2:
            raise StandardError('Fix')
        elif len(parts) == 2:
            name, type = parts
        else:
            name = parts[0]
            type = 'str'
        matcher = self.generate_matcher(type)
        return r'(?P<{name}>{matcher})'.format(name=name, matcher=matcher)

    def generate_matcher(self, type):
        return self.matchers[type]
