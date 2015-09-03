"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""


class StuboException(Exception):
    """ Base class for all :term:`exception response` objects."""

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __str__(self):
        return "%s: %s: %s" % (self.code, self.title, self.explanation)


############################################################
# 4xx client error
############################################################
class HTTPClientError(StuboException):
    """
    base class for the 400s, where the client is in error

    This is an error condition in which the client is presumed to be
    in-error.  This is an expected problem, and thus is not considered
    a bug.  A server-side traceback is not warranted.  Unless specialized,
    this is a '400 Bad Request'
    """
    code = 400
    title = 'Bad Request'
    explanation = ('The server could not comply with the request since '
                   'it is either malformed or otherwise incorrect.')


class UserExitModuleNotFound(HTTPClientError):
    pass


class TransformError(HTTPClientError):
    pass


############################################################
# 5xx Server Error
############################################################
class HTTPServerError(StuboException):
    """
    base class for the 500s, where the server is in-error

    This is an error condition in which the server is presumed to be
    in-error.  Unless specialized, this is a '500 Internal Server Error'.
    """
    code = 500
    title = 'Internal Server Error'
    explanation = (
        'The server has either erred or is incapable of performing '
        'the requested operation.')


def exception_response(status_code, **kw):
    """Creates an HTTP exception based on a status code. Example::

        raise exception_response(404) # raises an HTTPClientError exception.
        raise exception_response(5xx) # raises an HTTPServerError exception.

    The values passed as ``kw`` are provided to the exception's constructor.
    """
    if status_code > 499:
        exc = HTTPServerError(**kw)
    elif status_code > 399:
        exc = HTTPClientError(**kw)
    else:
        raise ValueError('status_code must be > 399, not {0}'.format(
            status_code))
    exc.code = status_code
    return exc
