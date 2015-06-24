from stubo.ext.xmlutils import XPathValue
from stubo.ext.xmlexit import XMLManglerExit

# exit that deals with responses with and without namespaces with various extractors 

def roll_dt(date_str):
    # source_date = '2014-12-10T15:30'
    # roll date part of string
    date_str = date_str.strip()
    return "{{% raw roll_date('{0}', as_date(recorded_on), as_date(played_on)) %}}".format(date_str)
                                                    
response_elements = dict(a=XPathValue('//response/b', extractor=lambda x: '{% raw getresponse_arg %}', element_index_func='position() - 1'),
                         b=XPathValue('//response/c', extractor=lambda x: "{{xmltree.xpath('/request/dt')[0].text}}"),
                         info_date=XPathValue('//response/info/date', extractor=roll_dt, element_index_func='count(../preceding-sibling::info) + 1'),
                         dt=XPathValue('//user:dt', extractor=roll_dt, element_index_func='count(../preceding-sibling::user:Body) + 1'),
                         userid=XPathValue('//user:InformationSystemUserIdentity/info:UserId',
                                           extractor=lambda x: "{{xmltree.xpath('/request2/user')[0].text}}"))
    
exit = XMLManglerExit(response_elements=response_elements,
                      response_namespaces=dict(user="http://www.my.com/userschema", 
                                               info="http://www.my.com/infoschema"))
    
def exits(request, context):
    return exit.get_exit(request, context)
    


        


