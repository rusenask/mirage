import logging
import datetime
from lxml import etree

from stubo.ext import rollDate

log = logging.getLogger(__name__)

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
<xsl:template match="//arrDate">
    <arrDate><xsl:value-of select="$arrival" /></arrDate>
</xsl:template>
<xsl:template match="//depDate">
    <depDate><xsl:value-of select="$departure" /></depDate>
</xsl:template>
</xsl:stylesheet>''')

def mangle_response(payload, **ext_info):
    # 'payload' will be either the request_text or response depending on when
    #  it is called.
    # 'ext_info' is a dictionary of needed data, for example:
    # ext_info = {
    #        'request_text' : request_text, 
    #        'stubbed_system_date' : stubbed_system_date,
    #        'recorded' : recorded_date,
    #        'system_date' : system_date,
    #        'ext' : 'matcher'
    #        'function' : 'put/stub' | 'get/response'
    #    }
    log.debug('mangle called for {0}'.format(ext_info['ext']))
    if ext_info['ext'] != 'response':
        raise ValueError("only expecting to mangle the response")
    
    result = payload
    
    func = ext_info.get('function')
    if func == 'get/response':    
        log.debug('get/response mangle - roll dates')
        recorded = ext_info['recorded']
        transform = etree.XSLT(stylesheet)
        log.debug('created transformer')
        doc = etree.fromstring(payload)
        log.debug('created doc')
        # convert depDate & arrDate
        arrival = doc.xpath('//arrDate')[0].text
        departure = doc.xpath('//depDate')[0].text
        log.debug('arrival: {0}, departure: {1}'.format(arrival, departure))
        today = datetime.date.today()  
        arrival = rollDate(arrival, recorded, today)
        departure = rollDate(departure, recorded, today)
        log.debug('arrival: {0}, departure: {1}'.format(arrival, departure))  
        arrival_param = etree.XSLT.strparam(arrival)
        departure_param = etree.XSLT.strparam(departure)                                                         
        result_tree = transform(doc, arrival=arrival_param, 
                                departure=departure_param)
        if transform.error_log:
            log.error(transform.error_log)
        result = unicode(result_tree)    
    return result
    

