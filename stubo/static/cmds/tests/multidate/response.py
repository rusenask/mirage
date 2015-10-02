from stubo.ext.xmlutils import XPathValue
from stubo.ext.xmlexit import XMLManglerExit

# exit that rolls response dates

def roll_dt(date_str):
    date_str = date_str.strip()
    # roll date part of string
    return "{{% raw roll_date('{0}', as_date({1}), as_date({2})) %}}".format(
                            date_str, 'recorded_on', 'played_on')
                                                    
response_elements = dict(deparature_date=XPathValue('//DepartureDate', extractor=roll_dt),
                         arrival_date=XPathValue('//ArrivalDate', extractor=roll_dt))
                        
namespaces = dict(soapenv="http://schemas.xmlsoap.org/soap/envelope/")  
                          
exit = XMLManglerExit(response_elements=response_elements,
                      response_namespaces=namespaces)
    
def exits(request, context):
    return exit.get_exit(request, context)
    


        


