"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import logging

log = logging.getLogger(__name__)

USER_EXIT_ENTRY_POINT = 'exits'


class UserExit(object):
    """UserExit API
    
    Subclass PutStub and/or GetResponse to hook custom user code into the
    stubo runtime. 
    
    The external user defined python module is loaded dynamically
    into stubo via the put/module REST call. The module is expected to have an
    'exits' function which can return an instance of UserExit when supplied with
    the request context. 
    
    For example:
          
    .. code-block:: python
    
        '''Example showing how the same request type but with different
        environmental data can be transformed by 'templating' the env values in
        the matcher & response during put/stub and transforming it with XSLT
        using the env values from request during get/response processing.
        
        e.g. request transformations
        
        <request>
        <a>a</a>
        <trans_id>1234</trans_id>
        <b>b</b>
        <user uuid="xxx">joe</user>
        <dt>2013-11-25</dt>
        </request>
        
        <response>
        <a>a</a>
        <trans_id>1234</trans_id>
        <b>b</b>
        <user uuid="xxx">joe</user>
        <dt>2013-11-25</dt>
        </response>
        
        to (in put/stub)
        
        <request>
        <a>a</a>
        <trans_id>***</trans_id>
        <b>b</b>
        <user uuid="***">***</user>
        <dt>***</dt>
        </request>
        
        <response> 
        <a>a</a>
        <trans_id>***</trans_id>
        <b>b</b>
        <user uuid="***">***</user>
        <dt>***</dt>
        </response>
        
        to (in get/response) for mary request
        
        <response>
        <a>a</a>
        <trans_id>12345</trans_id>
        <b>b</b>
        <user uuid="yyy">mary</user>
        <dt>2013-11-26</dt>
        </response>'''
    
        from lxml import etree
        from stubo.ext import eye_catcher
        from stubo.ext.user_exit import PutStub, GetResponse, ExitResponse
        
        stylesheet = etree.XML('''<?xml version="1.0"?>
        <xsl:stylesheet version="1.0"
          xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
          <xsl:output omit-xml-declaration="yes" encoding="UTF-8"/>
          <xsl:strip-space elements="*"/>
        <!-- Identity template : copy all text nodes, elements and attrs -->     
        <xsl:template match="@*|node()">
           <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
           </xsl:copy>
        </xsl:template>
        <!-- Match and replace env nodes -->
        <xsl:template match="//trans_id">
            <trans_id><xsl:value-of select="$trans_id" /></trans_id>
        </xsl:template>
        <xsl:template match="//user">
            <user uuid="{$uuid}"><xsl:value-of select="$user" /></user>
        </xsl:template>
        <xsl:template match="//dt">
            <dt><xsl:value-of select="$dt" /></dt>
        </xsl:template>
        </xsl:stylesheet>''')
    
    
        class ManglePutStub(PutStub):
            
            def __init__(self, request, context):
                PutStub.__init__(self, request, context)
                
            def wildcard_values(self, payload):
                transform = etree.XSLT(stylesheet)
                doc = etree.fromstring(payload)
                # use generic values during put/stub
                trans_id = user = dt = uuid = eye_catcher         
                result_tree = transform(doc, trans_id=trans_id, user=user, 
                                        dt=dt, uuid=uuid)
                if transform.error_log:
                    log.error(transform.error_log)
                result = unicode(result_tree)    
                return result       
                
            def doMatcher(self):
                stub = self.context['stub']
                wildcard_matchers = []
                for matcher in stub.contains_matchers():
                    # Note: there is only one matcher in this example
                    wildcard_matchers.append(self.wildcard_values(matcher)) 
                stub.set_contains_matchers(wildcard_matchers)
                return ExitResponse(self.request, stub)      
                        
            def doResponse(self):  
                stub = self.context['stub']
                response =  self.wildcard_values(stub.response_body()[0])
                stub.set_response_body(response)  
                return ExitResponse(self.request, stub)    
        
        class MangleGetResponse(GetResponse):
            
            def __init__(self, request, context):
                GetResponse.__init__(self, request, context)
                
            def substitute_request_values(self, payload):
                transform = etree.XSLT(stylesheet)
                doc = etree.fromstring(payload)
                request_doc = etree.fromstring(self.request.request_body()) 
                trans_id = request_doc.xpath('/request/trans_id')[0].text
                user = etree.XSLT.strparam(request_doc.xpath('///user')[0].text)
                uuid= etree.XSLT.strparam(request_doc.xpath('//user')[0].attrib['uuid'])
                dt = etree.XSLT.strparam(request_doc.xpath('///dt')[0].text)     
                result_tree = transform(doc, trans_id=trans_id, user=user, dt=dt, uuid=uuid)
                if transform.error_log:
                    log.error(transform.error_log)
                result = unicode(result_tree)    
                return result     
                
            def doMatcher(self):
                stub = self.context['stub']
                matchers = []
                for matcher in stub.contains_matchers():
                    # Note: there is only one matcher in this example
                    matchers.append(self.substitute_request_values(matcher)) 
                stub.set_contains_matchers(matchers)
                return ExitResponse(self.request, stub)      
                        
            def doResponse(self):  
                stub = self.context['stub']
                response =  self.substitute_request_values(stub.response_body()[0])
                stub.set_response_body(response)  
                return ExitResponse(self.request, stub)        
                
        def exits(request, context):
            if context['function'] == 'put/stub':
                return ManglePutStub(request, context)
            elif context['function'] == 'get/response':
                return MangleGetResponse(request, context)
    
    """

    def __init__(self, request, context, raise_on_error=True):
        self.request = request
        self.context = context
        self.template_processor = context['template_processor']
        self.raise_on_error = raise_on_error

    def run_exit(self):
        pass

    def run(self):
        log.debug('user exit called for {0}'.format(self.context))
        self.run_exit()
        return ExitResponse(self.request, self.context['stub'])

    def update(self, response):
        if response:
            self.request = response.request
            self.context['stub'] = response.stub

    def trace_update(self, func):
        trace = self.context['trace']
        msg = '=> {0}'.format(func.__name__)
        try:
            log.debug(msg)
            trace.info(msg)
            self.update(func())
        except Exception, e:
            err_msg = '{0}, error: {1}'.format(msg, e)
            log.warn(err_msg, exc_info=True)
            trace.error(err_msg)
            if self.raise_on_error:
                raise e

    def get_stub(self):
        return self.context['stub']

    def eval_text(self, templ, request, **kwargs):
        return self.template_processor.eval_text(templ, request, **kwargs)


class ExitResponse(object):
    """Return type of exit interface calls"""

    def __init__(self, request, stub):
        self.request = request
        self.stub = stub


class PutStub(UserExit):
    """PutStub user exit. Called during put/stub processing.
    """

    def __init__(self, request, context):
        UserExit.__init__(self, request, context)

    def run_exit(self):
        self.trace_update(self.doMatcher)
        self.trace_update(self.doResponse)

    def doMatcher(self):
        pass

    def doResponse(self):
        pass


class GetResponse(UserExit):
    """GetResponse user exit. Called during get/response processing. 
    """

    def __init__(self, request, context, raise_on_error=False):
        UserExit.__init__(self, request, context, raise_on_error=raise_on_error)

    def apply_matcher_template(self):
        trace = self.context['trace']
        log.debug('=> apply_matcher_template')
        trace.info('=> apply_matcher_template')
        try:
            matchers = self.get_stub().contains_matchers()
            evaluated_matchers = []
            for i in xrange(len(matchers)):
                matcher = matchers[i]
                matcher = self.eval_text(matcher, self.request, **self.context).decode('utf8')
                evaluated_matchers.append(matcher)
            self.context['stub'].set_contains_matchers(evaluated_matchers)
        except Exception, e:
            err_msg = 'apply_matcher_template error: {0}'.format(e)
            log.warn(err_msg)
            trace.error(err_msg)
            if self.raise_on_error:
                raise e

    def apply_response_template(self):
        trace = self.context['trace']
        msg = '=> apply_response_template'
        log.debug(msg)
        trace.info(msg)
        try:
            response_body = self.eval_text(self.context['stub'].response_body()[0],
                                           self.request, **self.context).decode('utf8')
            self.context['stub'].set_response_body(response_body)
        except Exception, e:
            err_msg = '{0}, error: {1}'.format(msg, e)
            log.warn(err_msg)
            trace.error(err_msg)

    def run_exit(self):
        stage = self.context.get('stage')
        trace = self.context['trace']

        if stage == 'matcher':
            self.trace_update(self.doMatcher)
            self.apply_matcher_template()
            self.trace_update(self.doMatcherRequest)

        elif stage == 'response':
            self.trace_update(self.doResponse)
            self.apply_response_template()

    def doMatcher(self):
        pass

    def doMatcherRequest(self):
        pass

    def doResponse(self):
        pass
