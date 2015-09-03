"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""


class TemplateProcessor(object):
    """ Derive from TemplateProcessor to provide an alternative template processor
        during transformations. See :class:`~stubo.ext.transformer.TransformerBase`
    """

    def eval_text(templ, request, **kwargs):
        """ Evaluate a template and return the result. 
        
         :Params:
          - `request`: the current request. See :class:`~stubo.model.request.Request`
          - `**kwargs`: additional keyword arguments including
                 stub - see :class:`~stubo.model.stub.Stub`
        """
        pass


class Hooks(object):
    """ Derive from Hooks class to provide alternative transformer.
    
        The Hook is defined via the stubo config file. The default implementation is
        
        hooks_cls = stubo.ext.transformer.StuboDefaultHooks
    """

    def make_transformer(self, stub):
        """ Factory method to create an instance of :class:`~stubo.ext.transformer.TransformerBase`
        
        :Params:
          - `stub`: stub to transform, see :class:`~stubo.model.stub.Stub`
        """
        pass
