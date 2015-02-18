from stubo.ext.xmlutils import StripNamespaceGetResponse
# removes any namespaces from the matcher & request before performing a match

def exits(request, context):
    if context['function'] == 'get/response':
        return StripNamespaceGetResponse(request, context)