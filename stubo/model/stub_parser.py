"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import logging

log = logging.getLogger(__name__)


class StubParser(object):
    def parse(self, body, url_args):
        pass

    def update_args(self, payload, url_args):
        args = payload.get('args', {})
        args.update(url_args)
        payload['args'] = args
        return payload


class JSONStubParser(StubParser):
    def parse(self, payload, url_args):
        if 'request' not in payload:
            raise ValueError("No 'request' definition found in body")
        body_patterns = payload['request'].get('bodyPatterns')
        if body_patterns and isinstance(body_patterns, list):
            # convert legacy JSON format
            payload['request']['bodyPatterns'] = body_patterns[0]
        if 'response' not in payload or not payload['response']:
            # default
            payload['response'] = dict(status=200)
        response_body = payload['response'].get('body')
        # we are kind of dependent on having a response body
        if not response_body:
            payload['response']['body'] = ""
        return self.update_args(payload, url_args)


class LegacyStubParser(StubParser):
    """
    LEGACY format
    ||textMatcher||<status>OK</status>||response||<response>YES</response>
    => JSON
    {
        "request": {
            "method": "POST",
            "bodyPatterns": [
                { "contains": ["<status>OK</status>"] }
            ]
            },
        "response": {
            "status": 200,
            "body": "<response>YES</response>"
        }
    }
    """

    SEPARATOR = '||'
    TEXT_MATCHER_KEY = 'textMatcher'
    RESPONSE_KEY = 'response'
    RESPONSE_SEP = '{0}{1}{0}'.format(SEPARATOR, RESPONSE_KEY)

    def parse(self, body, url_args):
        payload = dict(request=dict(method='POST',
                                    bodyPatterns=dict(contains=[])),
                       response=dict(status=200))
        parts = body.partition(LegacyStubParser.RESPONSE_SEP)
        if parts[1] != LegacyStubParser.RESPONSE_SEP or not parts[2]:
            raise ValueError('LegacyStubParser: NoResponseInBody')
        payload['response']['body'] = parts[-1]

        tokens = parts[0].split(LegacyStubParser.SEPARATOR)
        if tokens[0] != '':
            raise ValueError("LegacyStubParser: body does not start with separator '{0}'".format(
                LegacyStubParser.SEPARATOR))
        tokens = tokens[1:]

        key_value_pairs = zip(tokens[0::2], tokens[1::2])
        contains = payload['request']['bodyPatterns']['contains']
        for matcher_key, matcher in key_value_pairs:
            if matcher_key != LegacyStubParser.TEXT_MATCHER_KEY:
                raise ValueError("LegacyStubParser: Expected '{0}' not '{1}'".format(
                    LegacyStubParser.TEXT_MATCHER_KEY, matcher_key))
            contains.append(matcher)
        if len(contains) == 0:
            raise ValueError('LegacyStubParser: No matchers found')
        return self.update_args(payload, url_args)
