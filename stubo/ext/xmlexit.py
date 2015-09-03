"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import logging
import os
from lxml import etree
from stubo.ext import eye_catcher, parse_xml
from stubo.ext.user_exit import GetResponse, PutStub, ExitResponse
from stubo.ext.xmlutils import (
    strip_namespace, XMLMangler, parse_xml_strip_namespace
)
from stubo.utils import run_template

log = logging.getLogger(__name__)


class XMLManglerExit(object):
    """XMLManglerExit 
    
    1. Skip XML element and/or attribute values within the matching process 
    given identifying XPATH expressions. 
    
    And/Or
    
    2.  Mangle response element and/or attribute values given XPATH expressions. 
    Provide response_namespaces if your response contains namespaces. 
    
    For example:
          
    .. code-block:: python
    
        '''Example 1
           ---------
        
        Given this stub
        
        -- matcher --
        <user:Request xmlns:user="http://www.my.com/userschema">
        <user:dispatchTime>
                <user:businessSemantic>DTD</user:businessSemantic>
                <user:timeMode>U</user:timeMode>
                <user:dateTime>
                    <user:year>2014</user:year>
                    <user:month>10</user:month>
                    <user:day>01</user:day>
                    <user:hour>12</user:hour>
                    <user:minutes>24</user:minutes>
                    <user:seconds>46</user:seconds>
                </user:dateTime>
        </user:dispatchTime>
        </user:Request>
        
        -- response ---
        <?xml version="1.0" encoding="UTF-8"?>
        <XYZ>
        <a>goodbye</a>
        </XYZ>
        
        If we want to ignore or skip the date elements from the matching process
        and replace goodbye with hello in the response we would define the
        following user exit
        
        from stubo.ext.xmlutils import XPathValue, ignore_children
        from stubo.ext.xmlexit import XMLManglerExit
        
        elements = dict(dt=XPathValue('//dispatchTime/dateTime', ignore_children),
                        timeMode=XPathValue('//timeMode))

        response_elements = dict(a=XPathValue('//a', extractor=lambda x: 'hello'))
    
        exit = XMLManglerExit(elements=elements, response_elements=response_elements)
            
        def exits(request, context):
            return exit.get_exit(request, context) 
            
        Example 2
        ---------
        
        Given this response
        
        --- response ---
        <?xml version="1.0" encoding="UTF-8" ?> 
        <user:Response xmlns:user="http://www.my.com/userschema" xmlns:info="http://www.my.com/infoschema">
        <user:Body>
        <user:dt>2014-12-10T15:30</user:dt>
        <user:InformationSystemUserIdentity>
        <info:UserId>joe</info:UserId> 
        </user:InformationSystemUserIdentity>
        </user:Body>
        </user:Response>
        
        The following exit with transform the response to 
        
        1. Roll the dt date using url arg value supplied during the put/stub call along with the date obtained from the request.
        2. Use the user value in the request for UserId
        
        from stubo.ext.xmlutils import XPathValue
        from stubo.ext.xmlexit import XMLManglerExit
        
        def roll_dt(date_str):
            # date_str = '2014-12-10T15:30'
            # roll date part of string
            date_str = date_str.strip()
            return "{{% raw roll_date('{0}', as_date(recorded_on), as_date(played_on)) %}}".format(date_str)
                                                         
           
        response_elements = dict(dt=XPathValue('//user:dt', extractor=roll_dt),
                                 userid=XPathValue('//user:InformationSystemUserIdentity/info:UserId',
                                                   extractor=lambda x: "{{xmltree.xpath('/request2/user')[0].text}}"))
            
        exit = XMLManglerExit(response_elements=response_elements,
                              response_namespaces=dict(user="http://www.my.com/userschema", 
                                                       info="http://www.my.com/infoschema"))
            
        def exits(request, context):
            return exit.get_exit(request, context)                         
        '''
    """

    def __init__(self, elements=None, attrs=None, copy_attrs_on_match=True,
                 response_elements=None, response_attrs=None,
                 response_namespaces=None):
        """Create a XMLManglerExit.
        
        :Params:
          - `elements`  (optional): Matcher elements. A dict of element -> name to :class:`~stubo.ext.xmlutils.XPathValue`. An instance of :class:`dict`
          - `attrs`  (optional): Matcher attributes. A dict of attribute -> name to :class:`~stubo.ext.xmlutils.XPathValue`. An instance of :class:`dict`
          - `copy_attrs_on_match`  (optional): For matching elements, copy any element attributes. Defaults to True
          - `response_elements`  (optional): Response elements. A dict of element -> name to :class:`~stubo.ext.xmlutils.XPathValue`. An instance of :class:`dict`
          - `response_attrs`  (optional): Response attributes. A dict of attribute -> name to :class:`~stubo.ext.xmlutils.XPathValue`. An instance of :class:`dict`
          - `response_namespaces`  (optional): Response namespaces. An instance of :class:`dict`. 
        """

        self.mangler = self.response_mangler = None
        if elements or attrs:
            self.mangler = XMLMangler(elements=elements, attrs=attrs,
                                      copy_attrs_on_match=copy_attrs_on_match)
        if response_elements or response_attrs:
            self.response_mangler = XMLMangler(elements=response_elements,
                                               attrs=response_attrs,
                                               copy_attrs_on_match=True,
                                               namespaces=response_namespaces)

    def get_exit(self, request, context):
        """Return the user exit instance for this context.
        """
        if context['function'] == 'put/stub':
            if self.response_mangler:
                return PutStubMangleResponse(self.response_mangler,
                                             self.mangler, request, context)
            else:
                return XMLManglerPutStub(self.mangler, request, context)
        elif context['function'] == 'get/response':
            return XMLManglerGetResponse(self.mangler, request, context)


class XMLManglerPutStub(PutStub):
    def __init__(self, mangler, request, context):
        PutStub.__init__(self, request, context)
        self.mangler = mangler

    def doMatcher(self):
        stub = self.context['stub']
        if self.mangler:
            matchers = []
            for matcher in stub.contains_matchers():
                # use generic values during put/stub
                matchers.append(self.mangler.store(matcher))
            stub.set_contains_matchers(matchers)
        return ExitResponse(self.request, stub)


class PutStubMangleResponse(XMLManglerPutStub):
    def __init__(self, response_mangler, mangler, request, context):
        XMLManglerPutStub.__init__(self, mangler, request, context)
        if not response_mangler.all_xpaths_have_extractors():
            raise ValueError("XPATHs in response mangler should all have extractors")
        self.response_mangler = response_mangler

    def doResponse(self):
        stub = self.context['stub']
        response = self.response_mangler.store(stub.response_body()[0])
        stub.set_response_body(response)
        return ExitResponse(self.request, stub)


class XMLManglerGetResponse(GetResponse):
    def __init__(self, mangler, request, context):
        GetResponse.__init__(self, request, context)
        self.mangler = mangler

    def substitute_values(self, payload, excludes):
        """Mangle payload with values in the request based on the manglers 
           XPATH element and/or attr expressions. 
        """
        request_doc = parse_xml_strip_namespace(self.request.request_body())
        args = self.mangler.path_values(request_doc, excludes=excludes)
        if args:
            return self.mangler.mangle(payload, **args)
        else:
            return payload

    def doMatcherRequest(self):
        request = self.request
        if self.mangler:
            if self.mangler.extractor_names():
                request_body = self.substitute_values(request.request_body(),
                                                      excludes=[])
            else:
                request_body = strip_namespace(request.request_body())
            request.set_request_body_unicode(request_body)
        return ExitResponse(request, self.context['stub'])

    def doMatcher(self):
        stub = self.context['stub']
        if self.mangler:
            matchers = []
            for matcher in stub.contains_matchers():
                # replace stub matcher wildcards transformed during the put/stub
                # with values extracted from the request so the values will match
                matchers.append(self.substitute_values(matcher,
                                                       excludes=[]))
            stub.set_contains_matchers(matchers)
        return ExitResponse(self.request, stub)
