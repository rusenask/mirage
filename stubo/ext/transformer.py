"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import logging
from lxml import etree
from stubo.utils import as_date, compact_traceback, run_template
from stubo.exceptions import TransformError
from stubo.ext import roll_date, parse_xml, today_str  
from stubo.ext.user_exit import USER_EXIT_ENTRY_POINT
from .module import Module 
from .hooks import Hooks, TemplateProcessor

log = logging.getLogger(__name__)

class StuboDefaultHooks(Hooks):
    
    def make_transformer(self, stub):
        module = None
        if stub.module():
            module = Module(stub.host()).get(stub.module().get('name'), 
                                             stub.module().get('version'))    
        return Transformer(stub, module) 

def transform(stub, request, **kwargs):
    function = kwargs['function']
    stage = kwargs.get('stage')
    url_args = kwargs['url_args']
    trace = kwargs['trace']
    hooks = kwargs.pop('hooks')
    module_system_date = kwargs.get('module_system_date')
    try:
        transformer = hooks.make_transformer(stub)
        if module_system_date and isinstance(module_system_date, basestring):
            module_system_date = as_date(module_system_date)
        system_date = kwargs.get('system_date')
        if isinstance(system_date, basestring):
            system_date = as_date('system_date')   
        unsafevars = ('request', 'function', 'cache', 'stage',
                    'module_system_date', 'system_date', 'trace')
        url_args.update(x for x in stub.args().iteritems() if x[0] not in ('session', ))
        for var in unsafevars:
            url_args.pop(var, None)
            
        return transformer.transform(request,
                                     module_system_date=module_system_date, 
                                     system_date=system_date,
                                     function=function,
                                     cache=kwargs['cache'],
                                     stage=stage,
                                     trace=trace,
                                     **url_args)
    except Exception, e:
        _, t, v, tbinfo = compact_traceback()
        msg = u'error={0}, traceback is: ({1}: {2} {3})'.format(e, t, v, tbinfo)
        log.error(msg) 
        raise TransformError(code=400, title='Error transforming during '
            '{0} stage:{1}'.format(function, stage), traceback=msg)

class StuboTemplateProcessor(TemplateProcessor):
    
    def eval_text(self, templ, request, **kwargs):
        stub = kwargs['stub']
        kwargs['recorded'] = stub.recorded()
        recorded = kwargs.get('recorded')
        if recorded:
            kwargs['recorded'] = as_date(recorded) 
        return run_template(templ, 
            request=request,                
            request_text=request.request_body(), # legacy
            # utility functions   
            roll_date=roll_date,
            today=today_str,
            as_date=as_date,
            parse_xml=parse_xml,
            **kwargs)                                  
                                             
class TransformerBase(object):
    """ Transformer base class. 
    """ 
    
    def __init__(self, stub, module=None, template_processor=None):
        """ Create a transformer.
        
        :Params:
          - `stub`: the stub to transform. An instance of :class:`~stubo.model.stub.Stub`
          - `module`  (optional): the python module loaded via put/module that contains one or more user exits
          - `template_processor` (optional): template processor to use, an instance of :class:`~stubo.ext.hooks.TemplateProcessor`
        """
        self.module = module
        self.stub = stub
        self.template_processor = template_processor or StuboTemplateProcessor()
        
    def eval_text(self, templ, request, **kwargs):
        return self.template_processor.eval_text(templ, request, **kwargs) 

    def transform(self, request, **kwargs):
        stub = self.stub 
        trace = kwargs['trace']
        context = dict(stub=stub, template_processor=self.template_processor)
        try:
            # if the request is XML parse and make it available for templates 
            xmltree = etree.fromstring(request.request_body())
            context['xmltree'] = xmltree
        except Exception:
            pass  
        context.update(kwargs) 
        user_exit = self.get_user_exit(request, context)
        if user_exit:
            log.debug('run user exit')
            trace.info(u'run user exit => {0}'.format(str(user_exit)[1:-1]))
            response = user_exit.run()
            stub, request = response.stub, response.request
        elif context['function'] == 'get/response' \
                    and context['stage'] == 'response':
            # run stub response thru template even in the absence of an exit  
            stub = context['stub']
            trace.info("process response template")
            # eval_text returns utf8 so decode to unicode again here
            stub.set_response_body(self.eval_text(stub.response_body()[0], 
                                                  request, 
                                                  **context).decode('utf8')) 
        elif context['function'] == 'get/response' \
                    and context['stage'] == 'matcher' \
                    and stub.number_of_matchers() == 1:
            # run stub matcher thru template even in the absence of an exit  
            stub = context['stub']
            trace.info("process matcher template")
            # eval_text returns utf8 so decode to unicode again here
            stub.set_contains_matchers([self.eval_text(stub.contains_matchers()[0],
                                       request, **context).decode('utf8')])     
        return stub, request    
    
    def get_user_exit(self, request, context):
        """ Return a user exit for the request 
        
         :Params:
          - `request`: the current request. See :class:`~stubo.model.request.Request`
          - `context` (:class:`dict`): the request context including
                 stub - see :class:`~stubo.model.stub.Stub`
        
          Returns a :class:`~stubo.ext.user_exit.UserExit` instance or None.
        """
        pass    
                 
class Transformer(TransformerBase):
    """Standard Transformer 
    """
    
    def __init__(self, stub, module=None, template_processor=None):
        TransformerBase.__init__(self, stub, module, template_processor)
    
    def get_user_exit(self, request, context):
        if self.module:
            user_exit = getattr(self.module, USER_EXIT_ENTRY_POINT, None)
            if not user_exit:
                  raise TransformError(code=400, title="Error in transform get_user_exit, user exit module={0}, should have an 'exits' function".format(str(self.module)))     
            return user_exit(request, context) 
                              
        
                