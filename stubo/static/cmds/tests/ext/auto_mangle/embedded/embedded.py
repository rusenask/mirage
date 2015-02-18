import logging
from stubo.ext.xmlutils import XPathValue
from stubo.ext.xmlexit import XMLManglerExit

log = logging.getLogger(__name__)

# remove date from <Command> value
"""
<X>
    <Command>FQC1GBP/EUR/20Oct14</Command>
</X>​
"""        

elements = dict(screen_query=XPathValue('//X/Command', extractor=lambda x: x[:-7]))

    
exit = XMLManglerExit(elements=elements)
    
def exits(request, context):
    return exit.get_exit(request, context)
    


        


