import logging
from stubo.ext.xmlutils import XPathValue
from stubo.ext.xmlexit import XMLManglerExit

log = logging.getLogger(__name__)

element_index_func = 'count(../preceding-sibling::dateTime) + 1'
elements = dict(year=XPathValue('//dispatchTime/dateTime/year', extractor=lambda x: x, element_index_func=element_index_func),
                month=XPathValue('//dispatchTime/dateTime/month', element_index_func=element_index_func),
                day=XPathValue('//dispatchTime/dateTime/day', element_index_func=element_index_func),
                hour=XPathValue('//dispatchTime/dateTime/hour', element_index_func=element_index_func),
                minutes=XPathValue('//dispatchTime/dateTime/minutes', element_index_func=element_index_func),
                seconds=XPathValue('//dispatchTime/dateTime/seconds', element_index_func=element_index_func))

attrs = dict(y=XPathValue('//dispatchTime/date/@year'),
             m=XPathValue('//dispatchTime/date/@month'),
             d=XPathValue('//dispatchTime/date/@day'))
    
ignore = XMLManglerExit(elements=elements, attrs=attrs)
    
def exits(request, context):
    return ignore.get_exit(request, context)
    


        


