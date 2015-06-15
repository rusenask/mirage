# -*- coding: utf8 -*-
from stubo.testing import Base
import json

class TestMangling(Base):   
    
    def test_put_stub(self):
        self.http_client.fetch(self.get_url('/stubo/api/begin/session?scenario=xslt&session=s1&mode=record'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/put/module?name=/static/cmds/tests/ext/xslt/mangler.py'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
             
        self.http_client.fetch(self.get_url('/stubo/api/put/stub?session=s1&ext_module=mangler'), callback=self.stop,
            method="POST", body="""||textMatcher||<request><a>ba</a><trans_id>1234</trans_id><b>ba</b><user uuid="xxx">joe</user><dt>2013-11-25</dt></request>||response||<response><a>ba</a><trans_id>1234</trans_id><b>ba</b><user uuid="xxx">joe</user><dt>2013-11-25</dt></response>""")       
        response = self.wait()
        self.assertEqual(response.code, 200) 
        from stubo.model.db import Scenario
        scenario_db = Scenario(db=self.db)    
        stubs = list(scenario_db.get_stubs('localhost:xslt'))     
        self.assertEqual(len(stubs), 1)
        from stubo.model.stub import Stub
        stub = Stub(stubs[0]['stub'], 'localhost:xslt') 
        self.assertEqual(stub.contains_matchers()[0], 
                         u'<request><a>ba</a><trans_id>***</trans_id><b>ba</b><user uuid="***">***</user><dt>***</dt></request>\n')  
        self.assertEqual(stub.response_body()[0],
                         u'<response><a>ba</a><trans_id>***</trans_id><b>ba</b><user uuid="***">***</user><dt>***</dt></response>\n')
        from datetime import date  
        self.assertEqual(stub.module(), {
            u'system_date': str(date.today()), 
            u'recorded_system_date': str(date.today()),
            u'name': u'mangler'}) 
         
    def test_roundtrip(self):
        self.http_client.fetch(self.get_url('/stubo/api/exec/cmds?cmdfile=/static/cmds/tests/ext/xslt/first.commands'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], 
                         'application/json; charset=UTF-8')
        payload = json.loads(response.body)
        tracks = dict((x['request_params']['x'], x) for x in self.db.tracker.find() if 'x' in x.get('request_params'))
        track1 = tracks['1']
        self.assertEqual(track1['request_text'], 
"""<request>
<a>a</a>
<trans_id>1234</trans_id>
<b>b</b>
<user uuid="xxx">joe</user>
<dt>2013-11-25</dt>
</request>""")
        self.assertEqual(track1['stubo_response'], '<response><a>a</a><trans_id>1234</trans_id><b>b</b><user uuid="xxx">joe</user><dt>2013-11-25</dt></response>\n')
        track2 = tracks['2']
        self.assertEqual(track2['request_text'], 
"""<request>
<a>a</a>
<trans_id>12345</trans_id>
<b>b</b>
<user uuid="yyy">mary</user>
<dt>2013-11-26</dt>
</request>""")
        self.assertEqual(track2['stubo_response'], '<response><a>a</a><trans_id>12345</trans_id><b>b</b><user uuid="yyy">mary</user><dt>2013-11-26</dt></response>\n')


class TestSplitter(Base):   
    
    def test_put_stub(self):
        self.http_client.fetch(self.get_url('/stubo/api/put/module?name=/static/cmds/tests/ext/split/splitter.py'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/begin/session?scenario=split&session=split_1&mode=record'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/put/stub?session=split_1&ext_module=splitter'), callback=self.stop,
            method="POST", body="""||textMatcher||<a>
<pre>hello</pre>
<id>xxx</id>
<post>goodbye</post>
</a>||response||Hello {{1+1}} World""")       
        response = self.wait()
        self.assertEqual(response.code, 200) 
        from stubo.model.db import Scenario
        scenario_db = Scenario(db=self.db)    
        stubs = list(scenario_db.get_stubs('localhost:split'))     
        self.assertEqual(len(stubs), 1)
        from stubo.model.stub import Stub
        stub = Stub(stubs[0]['stub'], 'localhost:split')
        self.assertEqual(stub.contains_matchers(), 
                        [u'<a>\n<pre>hello</pre>\n', '\n<post>goodbye</post>\n</a>'])  
        self.assertEqual(stub.response_body()[0],
                         u'Hello {{1+1}} World')
        from datetime import date     
        self.assertEqual(stub.module(), {
            u'system_date': str(date.today()), 
            u'recorded_system_date': str(date.today()),                                 
            u'name': u'splitter'})
        
    def test_roundtrip(self):
        self.http_client.fetch(self.get_url('/stubo/api/exec/cmds?cmdfile=/static/cmds/tests/ext/split/1.commands'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], 
                         'application/json; charset=UTF-8')       
        tracks = [x for x in self.db.tracker.find() if x['function'] == 'get/response']
        self.assertEqual(tracks[0]['stubo_response'], 'Hello 2 World\n') 
     

class TestUserCache(Base):
     
    def test_put_stub(self):
        self.http_client.fetch(self.get_url('/stubo/api/put/module?name=/static/cmds/tests/ext/cache/text/example.py'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/begin/session?scenario=cache&session=cache_1&mode=record'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200) 
        
        stub = {
           "priority": 1, 
           "args": {
              "priority": "1", 
              "ext_module": "example"
           }, 
           "request": {
              "bodyPatterns": {
                 "contains": [
                    "<request>hello</request>\n"
                 ]
              }, 
              "method": "POST"
           }, 
           "response": {
              "body": "<response>0</response>\n", 
              "status": 200
           }
        }        
        import json
        self.http_client.fetch(self.get_url('/stubo/api/put/stub?session=cache_1&ext_module=example'), callback=self.stop,
        method="POST", body=json.dumps(stub),  headers={'Content-Type' : 'application/json'})
        response = self.wait()
        self.assertEqual(response.code, 200)
        from stubo.model.db import Scenario
        scenario_db = Scenario(db=self.db)    
        stubs = list(scenario_db.get_stubs('localhost:cache'))     
        self.assertEqual(len(stubs), 1)
        from stubo.model.stub import Stub
        stub = Stub(stubs[0]['stub'], 'localhost:cache') 
        self.assertEqual(stub.contains_matchers(), ['<request>hello</request>\n'])
        self.assertEqual(stub.response_body()[0], u'<response>0</response>\n')
        from datetime import date 
        self.assertEqual(stub.module(), {u'system_date': str(date.today()),
           u'recorded_system_date': str(date.today()),                                 
           u'name': u'example'})
        
    def test_roundtrip(self):      
        self.http_client.fetch(self.get_url('/stubo/api/exec/cmds?cmdfile=/static/cmds/tests/ext/cache/cache.yaml'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], 
                         'application/json; charset=UTF-8')
        payload = json.loads(response.body)
        tracks = dict((x['request_params']['x'], x) for x in self.db.tracker.find() if 'x' in x.get('request_params'))
        self.assertEqual(tracks['1']['stubo_response'], '<response>1</response>') 
        self.assertEqual(tracks['2']['stubo_response'], '<response>2</response>')
        self.assertEqual(tracks['3']['stubo_response'], '<response>3</response>')
        
class TestTextUserCache(Base):
     
    def test_put_stub(self):
        self.http_client.fetch(self.get_url('/stubo/api/put/module?name=/static/cmds/tests/ext/cache/text/example.py'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/begin/session?scenario=cache&session=cache_1&mode=record'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/put/stub?session=cache_1&ext_module=example'), callback=self.stop,
            method="POST", body="""||textMatcher||<request>hello</request>||response||<response>0</response>""")       
        response = self.wait()
        self.assertEqual(response.code, 200)
        from stubo.model.db import Scenario
        scenario_db = Scenario(db=self.db)    
        stubs = list(scenario_db.get_stubs('localhost:cache'))     
        self.assertEqual(len(stubs), 1)
        from stubo.model.stub import Stub
        stub = Stub(stubs[0]['stub'], 'localhost:cache') 
        self.assertEqual(stub.contains_matchers(), ['<request>hello</request>'])
        self.assertEqual(stub.response_body()[0], u'<response>0</response>')
        from datetime import date 
        self.assertEqual(stub.module(), {u'system_date': str(date.today()),
           u'recorded_system_date': str(date.today()),                                 
           u'name': u'example'})
        
    def test_roundtrip(self):      
        self.http_client.fetch(self.get_url('/stubo/api/exec/cmds?cmdfile=/static/cmds/tests/ext/cache/text/1.commands'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], 
                         'application/json; charset=UTF-8')
        payload = json.loads(response.body)
        tracks = dict((x['request_params']['x'], x) for x in self.db.tracker.find() if 'x' in x.get('request_params'))
        self.assertEqual(tracks['1']['stubo_response'], '<response>1</response>') 
        self.assertEqual(tracks['2']['stubo_response'], '<response>2</response>')
        self.assertEqual(tracks['3']['stubo_response'], '<response>3</response>')
            
class TestModule(Base):
    
    def _get_cmdq(self):
        from stubo.utils.command_queue import InternalCommandQueue
        return InternalCommandQueue(self.redis_server)
    
    def test_module_cant_compile(self):
        from stubo.exceptions import HTTPClientError
        self.http_client.fetch(self.get_url('/stubo/api/put/module?name=/static/cmds/tests/ext/bad_code.py'), self.stop)
        response = self.wait()
        self.assertEqual(response.headers["Content-Type"], 
                         'application/json; charset=UTF-8')
        self.assertEqual(response.code, 400)
        
    def test_missing_module_does_raise_error(self):
        from stubo.exceptions import HTTPClientError
        self.http_client.fetch(self.get_url('/stubo/api/begin/session?scenario=split1&session=s1&mode=record'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)       
        self.http_client.fetch(self.get_url('/stubo/api/put/stub?session=s1&ext_module=foo'), callback=self.stop,
            method="POST", body="||textMatcher||abcdef||response||a response")
        response = self.wait()
        self.assertEqual(response.code, 400)
        self.assertEqual(response.headers["Content-Type"], 
                         'application/json; charset=UTF-8')
        payload = json.loads(response.body)
        self.assertEqual(payload['error']['message'], 
                         "Error transforming during put/stub stage:put/stub")
                 
    def test_add(self):
        self.http_client.fetch(self.get_url('/stubo/api/put/module?name=/static/cmds/tests/ext/xslt/mangler.py'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], 
                         'application/json; charset=UTF-8')
        payload = json.loads(response.body)
        self.assertEqual(payload['data'], {"message": "added modules: ['localhost_mangler_v1']"})
        
    def test_add_no_change_to_code(self):
        self.http_client.fetch(self.get_url('/stubo/api/put/module?name=/static/cmds/tests/ext/xslt/mangler.py'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.http_client.fetch(self.get_url('/stubo/api/put/module?name=/static/cmds/tests/ext/xslt/mangler.py'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
       
    def test_list(self):
        self.http_client.fetch(self.get_url('/stubo/api/put/module?name=/static/cmds/tests/ext/xslt/mangler.py'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.http_client.fetch(self.get_url('/stubo/api/get/modulelist?name=mangler'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], 
                         'application/json; charset=UTF-8')
        payload = json.loads(response.body)
        self.assertEqual(1, payload['data']['info']["mangler"]['latest_code_version'])  
        
    def test_list_empty(self):
        self.http_client.fetch(self.get_url('/stubo/api/get/modulelist?name=mangler'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], 
                         'application/json; charset=UTF-8')
        payload = json.loads(response.body)
        self.assertEqual(0, payload['data']['info']["mangler"]['latest_code_version'])     
          
    def test_delete(self):
        self.http_client.fetch(self.get_url('/stubo/api/put/module?name=/static/cmds/tests/ext/xslt/mangler.py'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
    
        self.http_client.fetch(self.get_url('/stubo/api/delete/module?name=mangler'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        
        self.http_client.fetch(self.get_url('/stubo/api/get/modulelist?name=mangler'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], 
                         'application/json; charset=UTF-8')
        
        payload = json.loads(response.body)
        self.assertEqual(0, payload['data']['info']["mangler"]['latest_code_version'])    
        
class Test_xmlexit(Base):   
    
    def test_get_response_strip_ns(self):
        self.http_client.fetch(self.get_url('/stubo/api/exec/cmds?cmdfile=/static/cmds/tests/ext/get_response_strip_ns/record.commands'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/begin/session?scenario=strip_namespace&session=strip_namespace_1&mode=playback'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/get/response?session=strip_namespace_1'), callback=self.stop,
            method="POST", body="""<?xml version="1.0" encoding="UTF-8" ?> 
  <user2:Request xmlns:user2="http://www.my.com/userschema" xmlns:info="http://www.my.com/infoschema">
  <user2:Body>
  <user2:InformationSystemUserIdentity>
  <info:UserId xmlns:info="http://www.my.com/infoschema">joe</info:UserId> 
  </user2:InformationSystemUserIdentity>
  </user2:Body>
  </user2:Request>""")       
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.assertEqual(response.body, """<?xml version="1.0" encoding="UTF-8"?>
<XYZ>
<a>goodbye</a>
</XYZ>""")       
        
    def test_skip_xml(self):
        self.http_client.fetch(self.get_url('/stubo/api/exec/cmds?cmdfile=/static/cmds/tests/ext/auto_mangle/skip_xml/record.commands'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/begin/session?scenario=ignore_xml&session=ignore_xml1&mode=playback'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/get/response?session=ignore_xml1'), callback=self.stop,
            method="POST", body="""<user:Request xmlns:user="http://www.my.com/userschema">
<user:dispatchTime>
        <user:businessSemantic>DTD</user:businessSemantic>
        <user:timeMode>U</user:timeMode>
        <user:dateTime>
            <user:year>2014</user:year>
            <user:month>12</user:month>
            <user:day>25</user:day>
            <user:hour>09</user:hour>
            <user:minutes>30</user:minutes>
            <user:seconds>00</user:seconds>
        </user:dateTime>
        <user:date year="2014" month="12" day="25"></user:date>
</user:dispatchTime>
</user:Request>""")       
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.assertEqual(response.body, """<?xml version="1.0" encoding="UTF-8"?>
<XYZ>
<a>goodbye</a>
</XYZ>""")       
        
    def test_skip_xml_elements(self):
        self.http_client.fetch(self.get_url('/stubo/api/exec/cmds?cmdfile=/static/cmds/tests/ext/auto_mangle/skip_xml_elements/record.commands'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/begin/session?scenario=ignore_xml&session=ignore_xml1&mode=playback'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/get/response?session=ignore_xml1'), callback=self.stop,
            method="POST", body="""<user:Request xmlns:user="http://www.my.com/userschema">
<user:dispatchTime>
        <user:header>
         <user:transid>5</user:transid>
         <user:name>fred</user:name>
        </user:header>
        <user:empty_el></user:empty_el>
        <user:dateTime>
            <user:year>2014</user:year>
            <user:month>12</user:month>
            <user:day>25</user:day>
            <user:hour/>
            <user:minutes>30</user:minutes>
            <user:seconds>00</user:seconds>
        </user:dateTime>
</user:dispatchTime>
</user:Request>""")       
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.assertEqual(response.body, """<?xml version="1.0" encoding="UTF-8"?>
<XYZ>
<a>goodbye</a>
</XYZ>""")   
        
    def test_skip_xml_attrs(self):
        self.http_client.fetch(self.get_url('/stubo/api/exec/cmds?cmdfile=/static/cmds/tests/ext/auto_mangle/skip_xml_attrs/record.commands'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/begin/session?scenario=ignore_xml&session=ignore_xml1&mode=playback'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/get/response?session=ignore_xml1'), callback=self.stop,
            method="POST", body="""<user:Request xmlns:user="http://www.my.com/userschema">
<user:dispatchTime>
        <user:businessSemantic>DTD</user:businessSemantic>
        <user:timeMode>U</user:timeMode>
        <user:date year="2014" month="12" day="25"></user:date>
</user:dispatchTime>
</user:Request>""")       
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.assertEqual(response.body, """<?xml version="1.0" encoding="UTF-8"?>
<XYZ>
<a>goodbye</a>
</XYZ>""")      
        
    def test_embedded(self):
        self.http_client.fetch(self.get_url('/stubo/api/exec/cmds?cmdfile=/static/cmds/tests/ext/auto_mangle/embedded/record.commands'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/begin/session?scenario=embedded&session=embedded_play&mode=playback'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/get/response?session=embedded_play'), callback=self.stop,
            method="POST", body="""<X>
    <Command>FQC1GBP/EUR/25Oct14</Command>
</X>""")       
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.assertEqual(response.body, """<response>
<a>my response is kind</a>
</response>""")   
        
    def test_all(self):
        self.http_client.fetch(self.get_url('/stubo/api/exec/cmds?cmdfile=/static/cmds/tests/ext/auto_mangle/all/record.commands'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/begin/session?scenario=all&session=all_play&mode=playback'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/get/response?session=all_play'), callback=self.stop,
            method="POST", body="""<user:Request xmlns:user="http://www.my.com/userschema">
<user:dispatchTime>
        <user:businessSemantic>DTD</user:businessSemantic>
        <user:timeMode>U</user:timeMode>
        <user:dateTime>
            <user:year>2014</user:year>
            <user:month>12</user:month>
            <user:day>25</user:day>
            <user:hour>09</user:hour>
            <user:minutes>30</user:minutes>
            <user:seconds>00</user:seconds>
        </user:dateTime>
</user:dispatchTime>
</user:Request>""")       
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.assertEqual(response.body, """<XYZ><a>hello</a></XYZ>""")            
        
    def test_response(self):
        self.http_client.fetch(self.get_url('/stubo/api/exec/cmds?cmdfile=/static/cmds/tests/ext/auto_mangle/response/record.commands'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/begin/session?scenario=response&session=response_play&mode=playback'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.http_client.fetch(self.get_url('/stubo/api/get/response?session=response_play&getresponse_arg=foo'), callback=self.stop,
            method="POST", body="""<request>
<dt>2014-12-25</dt>
<user>fred</user>
</request>""")       
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.assertEqual(response.body, """<response><a>hello</a><b>foo</b><b>foo</b><c>2014-12-25</c></response>""")   
        
        self.http_client.fetch(self.get_url('/stubo/api/get/response?session=response_play&played_on=2014-12-15'), callback=self.stop,
            method="POST", body="""<request2>
<dt>2014-12-25</dt>
<user>fred</user>
</request2>""")       
        response = self.wait()
        self.assertEqual(response.code, 200)  
        self.assertEqual(response.body, """<user:Response xmlns:user="http://www.my.com/userschema" xmlns:info="http://www.my.com/infoschema"><user:Body><user:dt>2014-12-15T15:30</user:dt><user:InformationSystemUserIdentity><info:UserId>fred</info:UserId></user:InformationSystemUserIdentity></user:Body></user:Response>""")  
        
class TestUnicode(Base):  

    def test_non_ascii_matcher_and_response(self):
        self.http_client.fetch(self.get_url('/stubo/api/exec/cmds?cmdFile=/static/cmds/tests/ext/unicode/all.commands'), self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        self.assertEqual(response.headers["Content-Type"], 
                         'application/json; charset=UTF-8')
        payload = json.loads(response.body)
        tracks = list(self.db.tracker.find())
        for track in tracks:
            self.assertEqual(200, track.get('return_code'))
            if track.get('function') == 'get/response':
                self.assertEqual(u'''<response>
<FirstName>Können</FirstName>
<LastName>Umlaut</LastName>
</response>''', track.get('stubo_response'))                   