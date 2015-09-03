"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""
import logging
import os
from lxml import etree
from stubo.ext.user_exit import GetResponse, ExitResponse
from stubo.ext import parse_xml, eye_catcher
from stubo.utils import run_template

log = logging.getLogger(__name__)


def ignore_children(value):
    """extractor which ignores child elements"""
    return eye_catcher


class Value(object):
    pass


class XPathValue(Value):
    """XPathValue represents an XPATH expression to locate 1 or more elements
    or attributes. If an extractor is provided the result of the extractor will
    be used as the value for all matches in the transformation.
    """

    def __init__(self, xpath, extractor=None, name=None):
        """Create an XPathValue.
        
        :Params:
          - `xpath`: XPATH expression to locate an one or more XML elements or attributes.  An instance of :class:`string`
          - `extractor`  (optional): functor that can be used to transform the result of the XPATH value. Called with a single arg which is the XPATH result text of the corresponding matching element (xpath_result[X].text). e.g. extractor=lambda x: x.upper()
          - `name` (optional): element name to use, defaults to basename(xpath)
        """
        self.xpath = xpath
        self.extractor = extractor
        self.name = name or os.path.basename(xpath)
        self.parent = os.path.basename(os.path.dirname(xpath))


class StripNamespace(object):
    xslt = etree.XML('''<?xml version="1.0"?>
        <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
            <xsl:output indent="no" method="xml" encoding="utf-8" omit-xml-declaration="yes"/>
            <!-- Stylesheet to remove all namespaces from a document -->
            <!-- NOTE: this will lead to attribute name clash, if an element contains
                two attributes with same local name but different namespace prefix -->
            <!-- Nodes that cannot have a namespace are copied as such -->
        
            <!-- template to copy elements -->
            <xsl:template match="*">
                <xsl:element name="{local-name()}">
                    <xsl:apply-templates select="@* | node()"/>
                </xsl:element>
            </xsl:template>
        
            <!-- template to copy attributes -->
            <xsl:template match="@*">
                <xsl:attribute name="{local-name()}">
                    <xsl:value-of select="."/>
                </xsl:attribute>
            </xsl:template>
        
            <!-- template to copy the rest of the nodes -->
            <xsl:template match="comment() | text() | processing-instruction()">
                <xsl:copy/>
            </xsl:template>      
        </xsl:stylesheet>
        ''')

    def __init__(self):
        self.transform = etree.XSLT(StripNamespace.xslt)

    def strip(self, payload):
        transform = self.transform
        doc = parse_xml(payload)
        result_tree = transform(doc)
        if transform.error_log:
            log.error(transform.error_log)
        return unicode(result_tree).rstrip()


strip_ns = StripNamespace()


def strip_namespace(xml):
    return strip_ns.strip(xml)


def parse_xml_strip_namespace(xml):
    xml = strip_namespace(xml)
    return parse_xml(xml)


class StripNamespaceGetResponse(GetResponse):
    """ Ignore XML namespaces from the matching process in get/response 
    by performing an XSLT transformation to remove XML namespaces from the stub 
    matchers and source request."""

    def __init__(self, request, context):
        GetResponse.__init__(self, request, context)

    def doMatcher(self):
        stub = self.context['stub']
        matchers = []
        for matcher in stub.contains_matchers():
            matchers.append(strip_namespace(matcher))
        stub.set_contains_matchers(matchers)
        return ExitResponse(self.request, stub)

    def doMatcherRequest(self):
        request = self.request
        request.set_request_body_unicode(strip_namespace(
            self.request.request_body()))
        return ExitResponse(request, self.context['stub'])


class XMLMangler(object):
    xslt_template = '''<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns:str="http://exslt.org/strings" extension-element-prefixes="str"
  {% raw namespaces %}>
  <xsl:output omit-xml-declaration="yes" encoding="UTF-8"/>
  <xsl:strip-space elements="*"/>  
<xsl:template match="@*|node()">
   <xsl:copy>
    <xsl:apply-templates select="@*|node()" />
   </xsl:copy>
</xsl:template>
{% for name, path in attrs.iteritems() %}
    {% set path = path.xpath %}
    <xsl:template match="{{path}}">
      <xsl:attribute name="{{path.partition('@')[-1]}}">
           <xsl:choose>
            <xsl:when test="${{name}} != '___stubo_ignore___'">
                <xsl:value-of select="${{name}}" /> 
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="." /> 
            </xsl:otherwise>
        </xsl:choose>        
      </xsl:attribute>
    </xsl:template>
{% end %} 

{% for name, path in elements.iteritems() %}
    <xsl:template match="{{path.xpath}}">
       <xsl:element name="{{path.name}}"  namespace="{namespace-uri(.)}">    
        <xsl:choose>
            <xsl:when test="${{name}} != '___stubo_ignore___'">
                {% if copy_attrs_on_match %}
                  <xsl:apply-templates select="@*"/>
                {% end %} 
                
                <xsl:variable name="name" select="name()" />
                <xsl:variable name="element_index">
                  <xsl:value-of select="count(preceding::*[name()= $name]) + count(ancestor::*[name()= $name]) + 1" />
                </xsl:variable>              

                <xsl:variable name="value_count">
                  <xsl:value-of select="count(str:tokenize(string(${{name}}), ';'))"/>
                </xsl:variable>  
                                
                <xsl:variable name="element_index_value">
                    <xsl:if test="($element_index >= 1) and ($value_count > 1)">
                        <xsl:value-of select="str:tokenize(string(${{name}}), ';')[number($element_index)]" />  
                    </xsl:if>
                </xsl:variable>
                
                <xsl:choose>
                    <xsl:when test="($element_index_value != '')">
                        <xsl:value-of select="$element_index_value" />  
                    </xsl:when>
                    <xsl:otherwise>
                       <xsl:value-of select="${{name}}" /> 
                    </xsl:otherwise>
                </xsl:choose>      
            </xsl:when>
            <xsl:otherwise>
               <xsl:value-of select="." /> 
            </xsl:otherwise>
        </xsl:choose>    
      </xsl:element>
    </xsl:template>
{% end %}        
</xsl:stylesheet>'''

    def __init__(self, elements=None, attrs=None,
                 copy_attrs_on_match=True,
                 namespaces=None):
        """ elements is a iterable (name, xpath_expression) 
            attrs is a iterable (name, xpath_expression) 
            copy_attrs_on_match - copy matched element attributes? 
            namespaces - dict of possible namespace declarations
        """
        if not (elements or attrs):
            raise ValueError("Must specify a value for elements or attrs.")
        self.elements = elements or {}
        self.attrs = attrs or {}
        el_set = set(self.elements.keys())
        attr_set = set(self.attrs.keys())
        if not el_set.isdisjoint(attr_set):
            raise ValueError("Keys must be unique across elements and attrs. " \
                             "Found {0} in common".format(el_set & attr_set))
        self.namespaces = namespaces or {}
        namespace_decl = " ".join('xmlns:{0}="{1}"'.format(x[0], x[1]) for x in self.namespaces.iteritems())
        xslt = self.make_stylesheet(elements=self.elements, attrs=self.attrs,
                                    copy_attrs_on_match=copy_attrs_on_match,
                                    namespaces=namespace_decl)
        log.debug("xslt={0}".format(xslt))
        self.transform = etree.XSLT(etree.XML(xslt))

    def make_stylesheet(self, **kwargs):
        """ Dynamically generate XSLT stylesheet using elements or attrs
        """
        return run_template(self.xslt_template, basename=os.path.basename,
                            **kwargs)

    def mangle(self, xml_text, **kwargs):
        return self.mangle_xml(self.parse_xml(xml_text), **kwargs)

    def mangle_xml(self, xml_doc, **kwargs):
        """ Run the XSLT stylesheet to transform the XML using kwargs that
            correspond to elements or attrs defined in the ctor. 
            e.g. 
            elements = dict(y=XPathValue('//dateTime/year'), 
                            d=XPathValue('//dateTime/day'))
            attrs = dict(daylight=XPathValue('//day/@daylight-savings'))
            kwargs = y="'2014'", d="'15'", daylight="'false'"
            Note str values need to be contained in outer double quotes 
            alternatively use etree.XSLT.strparam which is required if the
            string contains embedded quotes.
        """
        log.debug('mangle_xml with args={0}'.format(kwargs))
        transform = self.transform
        log.debug("xml={0}".format(etree.tostring(xml_doc, pretty_print=True)))
        result_tree = transform(xml_doc, **kwargs)
        if transform.error_log:
            log.error(transform.error_log)
        # remove any newline added by the XSLT transform
        return unicode(result_tree).rstrip()

    def path_values_for(self, xml_doc, excludes, elements_or_attrs):
        def get_value(value, extractor):
            if not isinstance(value, basestring):
                # found element
                value = value.text or ''
            if path.extractor:
                value = path.extractor(value)
            return value

        def get_values(els, extractor):
            values = []
            for el in els:
                values.append(get_value(el, extractor))
            return values

        args = dict()
        for name, path in elements_or_attrs.iteritems():
            if name not in excludes or path.extractor == ignore_children:
                vals = xml_doc.xpath(path.xpath, namespaces=self.namespaces)
                # Note if the XPATH is not found we use the current 
                # value if there is a match for this path.
                value = '___stubo_ignore___'
                if vals:
                    if len(vals) > 1:
                        value = ";".join(get_values(vals, path.extractor))
                    else:
                        value = get_value(vals[0], path.extractor)
                else:
                    log.debug("Unable to find {0} using xpath={1} in request".format(name, path.xpath))
                log.debug('{0}={1}'.format(name, value))
                args[name] = etree.XSLT.strparam(value)

        log.debug('args={0}'.format(args))
        return args

    def path_values(self, xml_doc, excludes):
        args = dict()
        if self.elements:
            args.update(self.path_values_for(xml_doc, excludes, self.elements))
        if self.attrs:
            args.update(self.path_values_for(xml_doc, excludes, self.attrs))
        return args

    def extractor_names(self):
        names = []
        if self.elements:
            names.extend(x[0] for x in self.elements.iteritems() if x[1].extractor)
        if self.attrs:
            names.extend(x[0] for x in self.attrs.iteritems() if x[1].extractor)
        return names

    def skip_names(self):
        keys = []
        if self.elements:
            keys.extend(self.elements.keys())
        if self.attrs:
            keys.extend(self.attrs.keys())
        return tuple(set(keys) - set(self.extractor_names()))

    def has_extractors(self):
        return len(self.extractor_names()) != 0

    def parse_xml(self, xml):
        if self.namespaces:
            xml_doc = parse_xml(xml)
        else:
            xml_doc = parse_xml_strip_namespace(xml)
        return xml_doc

    def all_xpaths_have_extractors(self):
        # XPATHs in a response type mangler should all have extractors
        if self.elements:
            for name, path in self.elements.iteritems():
                if not path.extractor:
                    return False
        if self.attrs:
            for name, path in self.attrs.iteritems():
                if not path.extractor:
                    return False
        return True

    def store(self, xml):
        """XML stub to save. 
        """
        args = dict()
        if self.elements:
            for name, path in self.elements.iteritems():
                if not path.extractor:
                    args[name] = eye_catcher
        if self.attrs:
            for name, path in self.attrs.iteritems():
                if not path.extractor:
                    args[name] = eye_catcher

        xml_doc = self.parse_xml(xml)
        if self.has_extractors():
            extractor_values = self.path_values(xml_doc, excludes=args.keys())
            args.update(extractor_values)
        return self.mangle_xml(xml_doc, **args)
