from stubo.ext.user_exit import PutStub, GetResponse, ExitResponse

class SplitMatcher(PutStub):
    
    def __init__(self, request, context):
        PutStub.__init__(self, request, context)
        
    def doMatcher(self):
        stub = self.context['stub']
        matcher = stub.contains_matchers()[0]
        parts = matcher.partition('<id>xxx</id>')   
        stub.set_contains_matchers([parts[0], parts[-1]])
        return ExitResponse(self.request, stub)   
    
def exits(request, context):
    if context['function'] == 'put/stub':
        return SplitMatcher(request, context)

