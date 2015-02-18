from stubo.ext.xmlutils import XPathValue
from stubo.ext.xmlexit import XMLManglerExit

elements = dict(year=XPathValue('//dispatchTime/dateTime/year'),
                month=XPathValue('//dispatchTime/dateTime/month'),
                day=XPathValue('//dispatchTime/dateTime/day'),
                hour=XPathValue('//dispatchTime/dateTime/hour'),
                minutes=XPathValue('//dispatchTime/dateTime/minutes'),
                seconds=XPathValue('//dispatchTime/dateTime/seconds'))

response_elements = dict(a=XPathValue('//a', extractor=lambda x: 'hello'))
    
exit = XMLManglerExit(elements=elements, response_elements=response_elements)
    
def exits(request, context):
    return exit.get_exit(request, context)
    


        


