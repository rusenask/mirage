import unittest
from stubo.ext.xmlutils import XPathValue


class TestXMLMangler(unittest.TestCase):
    def _make(self, **kwargs):
        from stubo.ext.xmlutils import XMLMangler

        return XMLMangler(**kwargs)

    def test_ctor_empty(self):
        with self.assertRaises(ValueError):
            self._make()

    def test_ctor_elements(self):
        mangler = self._make(elements=dict(d=XPathValue('//dateTime/day')))
        self.assertTrue('d' in mangler.elements)

    def test_ctor_attrs(self):
        mangler = self._make(attrs=dict(daylight=XPathValue('@daylight-savings')))
        self.assertTrue('daylight' in mangler.attrs)

    def test_mangle(self):
        elements = {'d': XPathValue('//dateTime/day'), 'y': XPathValue('//dateTime/year')}
        mangler = self._make(elements=elements)
        xml = '<a><dateTime><year>2014</year><day>12</day></dateTime></a>'
        result = mangler.mangle(xml, d="'01'", y="'2015'")
        self.assertEqual(result, '<a><dateTime><year>2015</year><day>01</day></dateTime></a>')

    def test_mangle_ignore_non_matching_path(self):
        elements = {'d': XPathValue('//dateTime/day'), 'y': XPathValue('//dateTimexxx/year')}
        mangler = self._make(elements=elements)
        xml = '<a><dateTime><year>2014</year><day>12</day></dateTime></a>'
        result = mangler.mangle(xml, d="'01'", y="'2015'")
        self.assertEqual(result, '<a><dateTime><year>2014</year><day>01</day></dateTime></a>')

    def test_mangle_attr(self):
        attrs = {'daylight': XPathValue('@daylight-savings')}
        mangler = self._make(attrs=attrs)
        xml = '<a><dateTime><year>2014</year><day daylight-savings="true">12</day></dateTime></a>'
        result = mangler.mangle(xml, daylight="'false'")
        self.assertEqual(result, '<a><dateTime><year>2014</year><day daylight-savings="false">12</day></dateTime></a>')

    def test_mangle_attr2(self):
        attrs = {'daylight': XPathValue('//day/@daylight-savings')}
        mangler = self._make(attrs=attrs)
        xml = '<a><dateTime><year>2014</year><day daylight-savings="true">12</day></dateTime></a>'
        result = mangler.mangle(xml, daylight="'false'")
        self.assertEqual(result, '<a><dateTime><year>2014</year><day daylight-savings="false">12</day></dateTime></a>')

    def test_mangle_element_and_attr(self):
        attrs = {'daylight': XPathValue('//day/@daylight-savings')}
        elements = {'d': XPathValue('//dateTime/day'), 'y': XPathValue('//dateTime/year')}
        mangler = self._make(elements=elements, attrs=attrs)
        xml = '<a><dateTime><year>2014</year><day daylight-savings="true">12</day></dateTime></a>'
        result = mangler.mangle(xml, d="'01'", y="'2015'", daylight="'false'")
        self.assertEqual(result, '<a><dateTime><year>2015</year><day daylight-savings="false">01</day></dateTime></a>')

    def test_mangle_attrs_copied_on_matches(self):
        elements = {'d': XPathValue('//dateTime/day'), 'y': XPathValue('//dateTime/year')}
        mangler = self._make(elements=elements)
        xml = '<a name="foo"><dateTime><year>2014</year><day daylight="false">12</day></dateTime></a>'
        result = mangler.mangle(xml, d="'01'", y="'2015'")
        self.assertEqual(result,
                         '<a name="foo"><dateTime><year>2015</year><day daylight="false">01</day></dateTime></a>')

    def test_mangle_attrs_not_copied_on_matches(self):
        elements = {'d': XPathValue('//dateTime/day'), 'y': XPathValue('//dateTime/year')}
        mangler = self._make(elements=elements, copy_attrs_on_match=False)
        xml = '<a name="foo"><dateTime><year>2014</year><day daylight="false">12</day></dateTime></a>'
        result = mangler.mangle(xml, d="'01'", y="'2015'")
        self.assertEqual(result, '<a name="foo"><dateTime><year>2015</year><day>01</day></dateTime></a>')

    def test_mangle_date_with_embedded_quotes(self):
        elements = {'d': XPathValue('//dateTime/day'), 'y': XPathValue('//dateTime/year')}
        mangler = self._make(elements=elements)
        xml = '<a><dateTime><year>2014</year><day>12</day></dateTime></a>'
        from lxml import etree

        result = mangler.mangle(xml, d=etree.XSLT.strparam(""" It's "the first" """), y="'2015'")
        self.assertEqual(result, """<a><dateTime><year>2015</year><day> It's "the first" </day></dateTime></a>""")

    def test_mangle_with_wildcards(self):
        elements = {'d': XPathValue('//dateTime/day'), 'y': XPathValue('//dateTime/year')}
        mangler = self._make(elements=elements)
        xml = '<a><dateTime><year>2014</year><day>12</day></dateTime></a>'
        from stubo.ext import eye_catcher

        result = mangler.mangle(xml, d=eye_catcher, y="'2015'")
        self.assertEqual(result, '<a><dateTime><year>2015</year><day>***</day></dateTime></a>')

    def test_mangle_using_same_keys(self):
        elements = {'day': XPathValue('//dateTime/day'), 'year': XPathValue('//dateTime/year')}
        mangler = self._make(elements=elements)
        xml = '<a><dateTime><year>2014</year><day>12</day></dateTime></a>'
        result = mangler.mangle(xml, day="'01'", year="'2015'")
        self.assertEqual(result, '<a><dateTime><year>2015</year><day>01</day></dateTime></a>')

    def test_mangle_namespaces(self):
        elements = {'d': XPathValue('//user:dateTime/info:day'), 'y': XPathValue('//user:dateTime/info:year')}
        namespaces = dict(user="http://www.my.com/userschema",
                          info="http://www.my.com/infoschema")
        mangler = self._make(elements=elements, namespaces=namespaces)
        xml = """<a xmlns:user="http://www.my.com/userschema" xmlns:info="http://www.my.com/infoschema">
                 <user:dateTime><info:year>2014</info:year><info:day>12</info:day>
                 </user:dateTime></a>"""
        result = mangler.mangle(xml, d="'01'", y="'2015'")
        self.assertEqual(result,
                         '<a xmlns:user="http://www.my.com/userschema" xmlns:info="http://www.my.com/infoschema">'
                         '<user:dateTime><info:year>2015</info:year><info:day>01</info:day></user:dateTime></a>')

    def test_mangle_namespaces_ignore_non_matching_path(self):
        elements = {'d': XPathValue('//user:dateTime/info:day'), 'y': XPathValue('//user:dateTime/info:yearxxx')}
        namespaces = dict(user="http://www.my.com/userschema",
                          info="http://www.my.com/infoschema")
        mangler = self._make(elements=elements, namespaces=namespaces)
        xml = """<a xmlns:user="http://www.my.com/userschema" xmlns:info="http://www.my.com/infoschema">
                 <user:dateTime><info:year>2014</info:year><info:day>12</info:day>
                 </user:dateTime></a>"""
        result = mangler.mangle(xml, d="'01'", y="'2015'")
        self.assertEqual(result,
                         '<a xmlns:user="http://www.my.com/userschema" xmlns:info="http://www.my.com/infoschema">'
                         '<user:dateTime><info:year>2014</info:year><info:day>01</info:day></user:dateTime></a>')

    def test_mangle_element_and_attr_namespaces(self):
        attrs = {'daylight': XPathValue('//user:dateTime/info:day/@daylight-savings')}
        elements = {'d': XPathValue('//user:dateTime/info:day'), 'y': XPathValue('//user:dateTime/info:year')}
        namespaces = dict(user="http://www.my.com/userschema",
                          info="http://www.my.com/infoschema")
        mangler = self._make(elements=elements, attrs=attrs, namespaces=namespaces)
        xml = """<a xmlns:user="http://www.my.com/userschema" xmlns:info="http://www.my.com/infoschema">
                 <user:dateTime><info:year>2014</info:year><info:day daylight-savings="true">12</info:day>
                 </user:dateTime></a>"""
        result = mangler.mangle(xml, d="'01'", y="'2015'", daylight="'false'")
        self.assertEqual(result,
                         '<a xmlns:user="http://www.my.com/userschema" xmlns:info="http://www.my.com/infoschema">'
                         '<user:dateTime><info:year>2015</info:year>'
                         '<info:day daylight-savings="false">01</info:day></user:dateTime></a>')

    def test_store(self):
        elements = {'cmd': XPathValue('/A/Command')}
        mangler = self._make(elements=elements)
        result = mangler.store('<A><Command>FQC1GBP/EUR/25Oct14</Command></A>')
        self.assertEqual(result, '<A><Command>***</Command></A>')

    def test_store_with_extractor(self):
        elements = {'cmd': XPathValue('/A/Command', extractor=lambda x: x[:-7])}
        mangler = self._make(elements=elements)
        result = mangler.store('<A><Command>FQC1GBP/EUR/25Oct14</Command></A>')
        self.assertEqual(result, '<A><Command>FQC1GBP/EUR/</Command></A>')

    def test_store_with_extractor2(self):
        elements = {'cmd': XPathValue('/A/Command', extractor=lambda x: x[:-7]),
                    'cmd2': XPathValue('/A/Command2')}
        mangler = self._make(elements=elements)
        result = mangler.store('<A><Command>FQC1GBP/EUR/25Oct14</Command><Command2>FQC1GBP/EUR/25Oct14</Command2></A>')
        self.assertEqual(result, '<A><Command>FQC1GBP/EUR/</Command><Command2>***</Command2></A>')
