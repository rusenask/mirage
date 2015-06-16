from stubo.ext.user_exit import UserExit

class NoOp(UserExit):
    def __init__(self, request, context):
        UserExit.__init__(self, request, context) 
    
    def run_exit(self):
        pass
    
    def doMatcher(self):
        pass
        
    def doResponse(self):
        pass
        
def exits(request, context):
    return NoOp(request, context)    