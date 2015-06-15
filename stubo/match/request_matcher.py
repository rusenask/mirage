import re
import json
from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.helpers.hasmethod import hasmethod
from six.moves.urllib import parse as urlparse
from jsonpath_rw import jsonpath, parse
from stubo.ext import parse_xml

class RequestMatcher(BaseMatcher):

    def __init__(self, expected, component_name):
        self.expected = expected
        self.component_name = component_name
        
    def _get_value(self, request):
        return getattr(request, self.component_name)    

    def _matches(self, request):
        return self._get_value(request) == self.expected
        
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

class UrlArgs(RequestMatcher):

    def __init__(self, expected, exact_match=False):
        super(UrlArgs, self).__init__(expected, 'query')
        self.exact_match = exact_match

    def _matches(self, request):
        args = urlparse.parse_qs(self._get_value(request))
        if self.exact_match:
            return args == self.expected
        return all(item in args.items() for item in self.expected.items())
    
def has_query_args(query_args, exact_match=False):
    return UrlArgs(query_args, exact_match=exact_match)

def has_exactly_query_args(query_args):
    return has_query_args(query_args, True)

class DictMatcher(RequestMatcher):

    def __init__(self, expected, attr, exact_match=False):
        if not isinstance(expected, dict):
            expected = dict(eval(expected))
        super(DictMatcher, self).__init__(expected, attr)
        self.exact_match = exact_match

    def _matches(self, request):
        headers = self._get_value(request)
        if not isinstance(headers, dict):
            headers = dict(eval(headers))
        if self.exact_match:
            return headers == self.expected
        return all(headers.get(k) == v for k, v in self.expected.items())

def has_headers(query_args, exact_match=False):
    return DictMatcher(query_args, 'headers', exact_match=exact_match)

def has_exactly_headers(query_args):
    return has_headers(query_args, True)

class BodyContains(RequestMatcher):

    def __init__(self, expected):
        super(BodyContains, self).__init__(expected, "body_unicode")

    def _matches(self, request):
        request_body = self._get_value(request)
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

    :param substring: The string to search for.

    This matcher first checks whether the evaluated object is a string. If so,
    it checks whether it contains ``string``.

    Example::

        body_contains("def")

    will match "abcdefg".

    """
    return BodyContains(substring)

class UrlPattern(RequestMatcher):
    """URL pattern matcher for regular expressions"""

    def __init__(self, regex):
        super(UrlPattern, self).__init__(regex, "path")
        self.regex = re.compile(regex)

    def _matches(self, request):
        item = self._get_value(request)
        if not isinstance(item, basestring):
            return False

        return any(self.regex.finditer(item))

    def describe_to(self, description):
        description.append_text(u" urlPattern that matches regex: '{}'".format(self.expected))

    def describe_mismatch(self, actual, description):
        description.append_text(u" urlPattern '{}' does not match regex: '{}'"
                                .format(actual, self.expected))
        
def has_url_pattern(regex):
    """Matches if the request url matches the given regular expression.

    :param regex: The regex to search for.

    This matcher first checks whether the evaluated object is a string. If so,
    it checks whether the regex matches against the url path in the request.

    Example::

        has_url_pattern("/thing/matching/[0-9]+")

    will match url "/thing/matching/1".

    """
    return UrlPattern(regex)  

class BodyXPath(RequestMatcher):
    """XPath matcher for request body"""

    def __init__(self, xpath, namespaces=None):
        super(BodyXPath, self).__init__(xpath, "body_unicode")
        self.namespaces = namespaces or {}
        
    def _matches(self, request):
        xml = self._get_value(request)
        try:   
            doc = parse_xml(xml)
        except Exception, err:
            self.error = err
            return False
        
        found = doc.xpath(self.expected, namespaces=self.namespaces)
        return True if found else False

    def describe_to(self, description):
        description.append_text(u" body that matches xpath: '{}'".format(self.expected))

    def describe_mismatch(self, actual, description):
        description.append_text(u" body does not match xpath: '{}'".format(self.expected)) 
        if hasattr(self, 'error'):
            description.append_text(u" error: {0}".format(self.error))  
            
def body_xpath(xpath, namespaces=None):
    """Matches if any elements are returned evaluating the XPATH expression against the request body.

    :param xpath: The xpath expression.
    :param namespaces: dict of namespaces.

    This matcher first checks if the request unicode body can be parsed as XML. If so,
    it checks whether the XPATH expression returns any results.

    Example::

        body_has_xpath("//find/me")

    will match this request body "<find><me>hello</me></find>".

    """
    return BodyXPath(xpath, namespaces)     

class BodyJSONPath(RequestMatcher):
    """JSON Path matcher for request body"""

    def __init__(self, expr):
        super(BodyJSONPath, self).__init__(expr, "body_unicode")
        self.jsonpath_expr = parse(expr)
        
    def _matches(self, request):
        try:   
            payload = json.loads(self._get_value(request))
            found = self.jsonpath_expr.find(payload)
            return True if found else False
        except Exception, err:
            self.error = err
            return False

    def describe_to(self, description):
        description.append_text(u" body that matches json path: '{}'".format(self.expected))

    def describe_mismatch(self, actual, description):
        description.append_text(u" body does not match json path: '{}'".format(self.expected)) 
        if hasattr(self, 'error'):
            description.append_text(u" error: {0}".format(self.error)) 
            
def body_jsonpath(expr):
    """Matches if the JSON path expression evulates true against the request body.

    :param expt: The JSON path expression.
    """
    return BodyJSONPath(expr)                        
