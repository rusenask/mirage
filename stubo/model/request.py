"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
from stubo.utils import get_unicode_from_request, compute_hash


class StuboRequest(object):
    """Encapsulates the original source system request"""

    def __init__(self, request):
        """Create an instance using an HTTP request.
        
         :Params:
          - `request`: an HTTP request. See :class:`~tornado.httpclient.HTTPRequest`
        """
        self.headers = request.headers.get('Stubo-Request-Headers', '{}')
        self.uri = request.headers.get('Stubo-Request-URI', None)
        self.host = request.headers.get('Stubo-Request-Host', None)
        self.method = request.headers.get('Stubo-Request-Method', "POST")
        self.path = request.headers.get('Stubo-Request-Path', None)
        self.query = request.headers.get('Stubo-Request-Query', '')
        self.body = request.body
        self.body_unicode = get_unicode_from_request(request)

    def id(self):
        return compute_hash(u"".join([self.request_body(), self.path or "",
                                      self.method, self.query]))

    def request_body_unicode(self):
        """ Request body text converted into unicode
        """
        return self.body_unicode

    def request_body(self):
        """ Request body text
        """
        # always return body as unicode for now
        return self.request_body_unicode()

    def set_request_body_unicode(self, body):
        self.body_unicode = body

    def __eq__(self, other):
        if type(other) is type(self):
            return self.request_body() == other.request_body()
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return 'StuboRequest: uri={uri}, host={host}, method={method}, path=' \
               '{path}, query={query}, id={0}'.format(self.id(), **self.__dict__)

    def describe_to(self, desc):
        desc.append(str(self))
