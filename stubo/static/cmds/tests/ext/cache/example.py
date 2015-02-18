import logging
from stubo.ext.user_exit import GetResponse, ExitResponse

log = logging.getLogger(__name__)

class IncResponse(GetResponse):
    '''
    Increments a value in the response using the provided cache.
    '''    
    def __init__(self, request, context):
        GetResponse.__init__(self, request, context)
        
    def inc(self):
        cache = self.context['cache']
        val = cache.get('foo')
        log.debug('cache val = {0}'.format(val))
        if not val:
            val = 0
        val += 1
        cache.set('foo', val)
        return val                
                
    def doResponse(self):  
        stub = self.context['stub']
        stub.set_response_body('<response>{0}</response>'.format(self.inc()))  
        return ExitResponse(self.request, stub)        
        
def exits(request, context):
    if context['function'] == 'get/response':
        return IncResponse(request, context)
