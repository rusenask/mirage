import logging
from stubo.ext.xmlutils import XPathValue, ignore_children
from stubo.ext.xmlexit import XMLManglerExit

log = logging.getLogger(__name__)

elements = dict(header=XPathValue('//header', ignore_children),
                miss1=XPathValue('/you_wont_find_me', ignore_children),
                miss2=XPathValue('//empty_el'),
                year=XPathValue('//dispatchTime/dateTime/year'),
                month=XPathValue('//dispatchTime/dateTime/month'),
                day=XPathValue('//dispatchTime/dateTime/day'),
                hour=XPathValue('//dispatchTime/dateTime/hour'),
                minutes=XPathValue('//dispatchTime/dateTime/minutes'),
                seconds=XPathValue('//dispatchTime/dateTime/seconds'))
    
ignore = XMLManglerExit(elements=elements)
    
def exits(request, context):
    return ignore.get_exit(request, context)
    


        


