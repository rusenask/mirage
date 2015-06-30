import logging
from stubo.ext.xmlutils import XPathValue
from stubo.ext.xmlexit import XMLManglerExit

log = logging.getLogger(__name__)

elements = dict(year=XPathValue('//dispatchTime/dateTime/year', extractor=lambda x: x),
                month=XPathValue('//dispatchTime/dateTime/month'),
                day=XPathValue('//dispatchTime/dateTime/day'),
                hour=XPathValue('//dispatchTime/dateTime/hour'),
                minutes=XPathValue('//dispatchTime/dateTime/minutes'),
                seconds=XPathValue('//dispatchTime/dateTime/seconds'))

attrs = dict(y=XPathValue('//dispatchTime/date/@year'),
             m=XPathValue('//dispatchTime/date/@month'),
             d=XPathValue('//dispatchTime/date/@day'))
    
ignore = XMLManglerExit(elements=elements, attrs=attrs)
    
def exits(request, context):
    return ignore.get_exit(request, context)
    


        


