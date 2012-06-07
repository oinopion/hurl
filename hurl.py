from django.core.urlresolvers import RegexURLPattern
from django.core.exceptions import ImproperlyConfigured

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

class Parser(object):

    def parse(self, input_url):
        parts = []

        text_part = ""
        started_parameter = False

        for character in input_url:
            if character == ' ':
                if started_parameter and text_part:
                    text_part += character
                continue
            elif character in ['/', '<']:
                if started_parameter:
                    raise ImproperlyConfigured("Missing '>'.")
                if character == '<':
                    started_parameter = True
                if text_part:
                    parts.append(StaticPart(text_part))
                    text_part = ''
            elif character == '>':
                if not started_parameter:
                    raise ImproperlyConfigured("Missing '<'.")
                started_parameter = False

                name_type = [part.strip() for part in text_part.split(':')]
                if len(name_type) > 2:
                    raise ImproperlyConfigured("Cannot use more than one colon in parameter.")
                elif len(name_type) == 1:
                    name_type.append(None)

                [name, type] = name_type
                if name and len(name.strip().split(" ")) > 1:
                    raise ImproperlyConfigured("Name of parameter cannot contain spaces.")

                if type and len(type.strip().split(" ")) > 1:
                    raise ImproperlyConfigured("Type of parameter cannot contain spaces.")

                parts.append(PatternPart(name, type))
                text_part = ""
            else:
                text_part += character
        if started_parameter:
            raise ImproperlyConfigured("Missing '>'.")
        if text_part.strip() != '':
            parts.append(StaticPart(text_part))
        return parts


class StaticPart(object):

    def __init__(self, pattern):
        self.pattern = pattern

    def __eq__(self, other):
        if isinstance(other, StaticPart):
            return self.pattern == other.pattern
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result


class PatternPart(object):

    def __init__(self, name=None, type=None):
        if name != None and type != None:
            self.name = name
            self.type = name
        elif name != None:
            self.name = name
            self.type = name
        else:
            self.name = ''
            self.type = type

    def __eq__(self, other):
        if isinstance(other, PatternPart):
            return (self.name == other.name)# and self.type == other.type)
        return NotImplemented

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
