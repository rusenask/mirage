import logging
from stubo.ext.xmlutils import XPathValue
from stubo.ext.xmlexit import XMLManglerExit

log = logging.getLogger(__name__)

attrs = dict(year=XPathValue('//dispatchTime/date/@year'),
             month=XPathValue('//dispatchTime/date/@month'),
             day=XPathValue('//dispatchTime/date/@day'))
    
ignore = XMLManglerExit(attrs=attrs)
    
def exits(request, context):
    return ignore.get_exit(request, context)
    


        


