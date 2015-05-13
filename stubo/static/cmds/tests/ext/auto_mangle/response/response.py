from stubo.ext.xmlutils import XPathValue
from stubo.ext.xmlexit import XMLManglerExit

# exit that deals with responses with and without namespaces with various extractors 

def roll_dt(source_date):
    # source_date = '2014-12-10T15:30'
    # roll date part of string
    return "{{% raw roll_date('{0}', as_date(recorded_on), as_date(played_on)) %}}".format(source_date)
                                                 
   
response_elements = dict(a=XPathValue('//response/b', extractor=lambda x: '{% raw getresponse_arg %}'),
                         b=XPathValue('//response/c', extractor=lambda x: "{{xmltree.xpath('/request/dt')[0].text}}"),
                         dt=XPathValue('//user:dt', extractor=roll_dt),
                         userid=XPathValue('//user:InformationSystemUserIdentity/info:UserId',
                                           extractor=lambda x: "{{xmltree.xpath('/request2/user')[0].text}}"))
    
exit = XMLManglerExit(response_elements=response_elements,
                      response_namespaces=dict(user="http://www.my.com/userschema", 
                                               info="http://www.my.com/infoschema"))
    
def exits(request, context):
    return exit.get_exit(request, context)
    


        


