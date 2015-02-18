import logging
import os
from lxml import etree

from stubo.ext import eye_catcher
from stubo.ext.user_exit import PutStub, GetResponse, ExitResponse

log = logging.getLogger(__name__)

"""
    Example showing how the same request but with different
    environmental data can be transformed by 'templating' the env values in
    the matcher & response during put/stub and transforming it with XSLT using 
    the env values from request_text during get/response 
  
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
    </response>
"""  

stylesheet = etree.XML('''<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output omit-xml-declaration="yes" encoding="UTF-8"/>
  <xsl:strip-space elements="*"/>
<!-- Identity template : copy all text nodes, elements and attributes -->     
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
        log.debug('created transformer')
        doc = etree.fromstring(payload)
        log.debug('created doc')
        # use generic values during put/stub
        trans_id = user = dt = uuid = eye_catcher   
        log.debug('user: {0}, trans_id: {1}, dt: {2}, uuid: {3}'.format(user, 
                                                            trans_id, dt, uuid))        
        result_tree = transform(doc, trans_id=trans_id, user=user, dt=dt, uuid=uuid)
        if transform.error_log:
            log.error(transform.error_log)
        result = unicode(result_tree)    
        log.debug(u'transformed to {0}'.format(result))  
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
        log.debug('created transformer')
        doc = etree.fromstring(payload)
        log.debug('created doc')
        request_doc = etree.fromstring(self.request.request_body()) 
        trans_id = request_doc.xpath('/request/trans_id')[0].text
        user = etree.XSLT.strparam(request_doc.xpath('///user')[0].text)
        uuid= etree.XSLT.strparam(request_doc.xpath('//user')[0].attrib['uuid'])
        dt = etree.XSLT.strparam(request_doc.xpath('///dt')[0].text)
         
        log.debug('user: {0}, trans_id: {1}, dt: {2}, uuid: {3}'.format(user, 
                                                            trans_id, dt, uuid))        
        result_tree = transform(doc, trans_id=trans_id, user=user, dt=dt, uuid=uuid)
        if transform.error_log:
            log.error(transform.error_log)
        result = unicode(result_tree)    
        log.debug(u'transformed to {0}'.format(result))  
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
