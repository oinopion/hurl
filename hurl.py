import re
from collections import Callable
from django.conf.urls import url, include, patterns as urls_patterns
from django.core.exceptions import ImproperlyConfigured

__all__ = 'Hurl', 'ViewSpec', 'v', 'patterns'

DEFAULT_MATCHER = 'slug'
DEFAULT_MATCHERS = {
    'int': r'\d+',
    'slug': r'[\w-]+',
    'str': r'[^/]+',
}

PATH_SEPARATOR = '/'
PARAM_SEPARATOR = ':'
DEFAULT_MATCHER_KEY = '__default__'
PATTERN_RE = re.compile(r'<([\w:]+?)>')
NAMED_TEMPLATE = r'(?P<{name}>{matcher})'
ANON_TEMPLATE = r'({matcher})'


def patterns(prefix, pattern_dict):
    h = Hurl()
    return h.patterns(prefix, pattern_dict)


def include(arg, namespace=None, app_name=None):
    return ViewSpec(view=(arg, namespace, app_name))


class Hurl(object):
    def __init__(self, name_prefix=''):
        self.matchers = Matchers()
        self.name_prefix = name_prefix
        self.transcriber = PatternTranscriber(self.matchers)

    def patterns(self, prefix, pattern_dict):
        urls = self.urls(pattern_dict)
        return urls_patterns(prefix, *urls)

    def urls(self, pattern_dict):
        return tuple(self._urls(pattern_dict))

    def _urls(self, pattern_dict):
        tree = build_tree(pattern_dict)
        urls = tree.urls(self.transcriber)
        for pattern, view_spec, view_params in urls:
            pattern = finalize_pattern(pattern)
            view = view_spec.view
            kwargs = view_spec.view_kwargs
            name = self._view_name(view_spec)
            yield pattern, view, kwargs, name

    def _view_name(self, view_spec):
        name = view_name(view_spec.view, view_spec.name)
        if name and self.name_prefix:
            name = '{prefix}_{name}'.format(prefix=self.name_prefix, name=name)
        return name

    @property
    def default_matcher(self):
        return self.matchers.default_matcher_name

    @default_matcher.setter
    def default_matcher(self, value):
        self.matchers.default_matcher_name = value

    def include(self, arg, namespace=None, app_name=None):
        return include(arg, namespace, app_name)

# internals

def build_tree(url_conf, pattern=''):
    if isinstance(url_conf, (basestring, Callable)):
        url_conf = ViewSpec(url_conf)
    if isinstance(url_conf, ViewSpec):
        return UrlLeaf(pattern, view=url_conf)
    if isinstance(url_conf, dict):
        url_conf = url_conf.items()
    node = UrlNode(pattern)
    for sub_pattern, sub_conf in url_conf:
        child = build_tree(sub_conf, sub_pattern)
        node.children.append(child)
    return node


class ViewSpec(object):
    def __init__(self, view, name=None, view_kwargs=None):
        self.view = view
        self.name = name
        self.view_kwargs = view_kwargs

v = ViewSpec # convenient alias


class UrlNode(object):
    def __init__(self, pattern):
        self.pattern = pattern
        self.children = []

    def urls(self, transcribe):
        pattern, params = transcribe(self.pattern)
        for child in self.children:
            child_urls = list(child.urls(transcribe))
            for url in child_urls:
                yield self.merge_child_url(pattern, params, url)

    def merge_child_url(self, pattern, params, child_url):
        sub_pattern, view_spec, sub_params = child_url
        if not sub_pattern:
            sub_pattern = pattern
        elif pattern:
            sub_pattern = PATH_SEPARATOR.join((pattern, sub_pattern))
        sub_params = sub_params.copy()
        sub_params.update(params)
        return sub_pattern, view_spec, sub_params


class UrlLeaf(object):
    def __init__(self, pattern, view):
        self.pattern = pattern
        self.view = view

    def urls(self, transcribe):
        pattern, params = transcribe(self.pattern)
        yield pattern, self.view, params


def view_name(view, name=None):
    if name:
        return name
    if isinstance(view, basestring):
        return view.split('.')[-1]
    if isinstance(view, Callable):
        return getattr(view, 'func_name')


def finalize_pattern(pattern):
    if pattern == '':
        return r'^$'
    return r'^{url}/$'.format(url=pattern)


class PatternTranscriber(object):
    def __init__(self, matchers):
        self.matchers = matchers
        self.params = None

    def transcribe_pattern(self, pattern):
        self.params = {}
        transcribed = PATTERN_RE.sub(self.replace, pattern)
        return transcribed, self.params

    __call__ = transcribe_pattern

    def replace(self, match):
        param, type = self.split_param(match.group(1))
        self.params[param] = type
        matcher = self.matchers.matcher(param, type)
        template = NAMED_TEMPLATE if param else ANON_TEMPLATE
        return template.format(matcher=matcher, name=param)

    def split_param(self, param_string):
        if param_string.count(PARAM_SEPARATOR) > 1:
            raise ImproperlyConfigured('Syntax error: %s' % param_string)
        param, _, type = param_string.partition(':')
        return param, type


class Matchers(dict):
    def __init__(self):
        self.default_matcher_name = DEFAULT_MATCHER
        super(Matchers, self).__init__(DEFAULT_MATCHERS)

    def default_matcher(self):
        return self[self.default_matcher_name]

    def matcher(self, param, type):
        if type:
            if type in self:
                return self[type]
            else:
                raise ImproperlyConfigured('Matcher not known: %s' % type)
        else:
            if param in self:
                return self[param]
            else:
                return self.default_matcher()
