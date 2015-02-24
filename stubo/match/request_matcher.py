from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.helpers.hasmethod import hasmethod
from six.moves.urllib import parse as urlparse

class RequestMatcher(BaseMatcher):

    def __init__(self, expected, component_name):
        self.expected = expected
        self.component_name = component_name

    def _matches(self, request):
        expected_attr_value = getattr(request, self.component_name)
        return expected_attr_value == self.expected
        
    def describe_to(self, description):
        description.append_text("a request with {0}: {1}".format(
            self.component_name,
            self.expected,
        ))
        return description

def has_host(host):
    return RequestMatcher(host, "host")

def has_method(method):
    return RequestMatcher(method, "method")

def has_path(path):
    return RequestMatcher(path, "path")


class HasQueryArgsMatcher(RequestMatcher):

    def __init__(self, expected, exact_match=False):
        super(HasQueryArgsMatcher, self).__init__(expected, "query")
        self.exact_match = exact_match

    def _matches(self, request):
        qs_args = urlparse.parse_qs(request.query)
        if self.exact_match:
            return qs_args == self.expected
        return all(item in qs_args.items() for item in self.expected.items())


def has_query_args(query_args):
    return HasQueryArgsMatcher(query_args)

def has_exactly_query_args(query_args):
    return HasQueryArgsMatcher(query_args, exact_match=True)

class BodyContains(RequestMatcher):

    def __init__(self, expected):
        super(BodyContains, self).__init__(expected, "body_unicode")

    def _matches(self, request):
        request_body = request.body_unicode
        if not isinstance(request_body, basestring) and not hasmethod(request_body, 'find'):
            return False
        return self._contains(self.expected, request_body)
    
    def _contains(self, x, y):
        """x in y?
        x and y should both be unicode
        """
        x = u''.join(x.split()).strip()
        y = u''.join(y.split()).strip()
        return y.find(x) >= 0

    def relationship(self):
        return 'containing'


def body_contains(substring):
    """Matches if object is a string containing a given string.

    :param string: The string to search for.

    This matcher first checks whether the evaluated object is a string. If so,
    it checks whether it contains ``string``.

    Example::

        body_contains("def")

    will match "abcdefg".

    """
    return BodyContains(substring)
