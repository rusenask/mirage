.. advanced

********
Stubbing
********

Add Delay to a Response
=======================

To emulate response times of systems being stubbed, one can set a delay on stubs. Delays are set on the stub response, not on the request to stubo. This is because one request into the system being tested can result in several back-end/stubo calls, each of which might need different delay settings.

Mirage provides reusable delay_policy objects which can be used across many stubs and across sessions. The delay_policy can be altered on the fly, during a load/performance test if desired. There are currently two delay_policy types to choose from. (1) fixed, and (2)random with mean and standard deviation.

A fixed delay policy can be created or modified with a commnand such as: ::

    put/delay_policy?name=a_fixed_delay_policy&delay_type=fixed&milliseconds=200

Note that the value for the 'name' can be set to any string and is used again in the put/stub.
A variable delay can be set up as follows: ::

    put/delay_policy?name=a_normalvariate_delay_policy&delay_type=normalvariate&mean=100&stddev=50

Allowed 'delay type' values are 'fixed' and 'normalvariate'
The next step is to use the delay policy when loading stubs, eg.: ::

    put/stub?session=abc&delay_policy=a_fixed_delay_policy

* Whenever the stub above is used, the named delay policy will be applied.
* Delay policies may be altered on the fly, during a test run if desired. To change a delay on the fly, simply 
  repeat the put/delay_policy command with a different value. Typically this would be done directly by the 
  test tool, rather than from a command file.
* Delay policies can be used across multiple sessions. This allows for easier alteration of policies where many sessions use the same policy. It also means that you should name policies carefully and only alter or share policies you are in control of.

Matching
========

Mirage currently supports various types of matchers.

Body contains matching
======================

One or more matchers can be defined whereby all matchers must be contained in the request to return a specified response. 
A typical difficulty with system requests is that they often contain superfluous information such as session IDs 
or time stamps that get in the way of matching a request to the desired response. One way Mirage can solve this problem is 
by the use of 'matchers'. Matchers are parts of the request that matter to you, only what is needed to find the correct
response file.

For example, a request may include: ::

  <sessionid>123456</sessionid>
    <transactionid>0987654321-9999</transactionid>
        <departurestartdatetime>2009-10-24T00:00:00+00:00</departurestartdatetime>
              <flightnumber>0455</flightnumber>

Of these 4 lines only the last 2 matter, the first 2 lines will differ from one request to the next and be set by the
system making the request. This request then will be different each time it is made. How can one easily match a
request like this to a canned response file without writing code for each request/response pair ?
The solution used by Mirage is to not store request/response file pairs, but rather store matchers and the
response. In the case above the matchers would be: ::

                <departurestartdatetime>2009-10-24T00:00:00+00:00</departurestartdatetime>
                  <flightnumber>0455</flightnumber>

Mirage contains code which will take a request as input, search for the response with the best matchers. Every 
matcher must be contained in the request to be a match. When a match is found the corresponding response is served
back.

*All matchers must be present in the request to make a match.* Mirage will return the response from the first match if there is more than one possible match. Note that whitespace and carriage returns are ignored when
matching.

Alternatives to removing parts of the request you don't want to match on are 

1. using a matcher template to substitute ids or dates etc from the request into the matcher OR 
2. using a user exit to run custom code. A convenience class XMLManglerExit is provided for XML payloads to ignore XMl elements and/or attributes from the matching process.

Templated Matcher
=================

This is an example of a template matcher than extracts values from the request into the matcher. 
The xmltree object is an lxml parsed root element passed into the template. ::

    <request>
    <transid>{{xmltree.xpath('/request/transid')[0].text}}</transid>
    <dt>2009-10-24T00:00:00+00:00</dt>
    <flightnumber>0455</flightnumber>
    </request>



Templated Responses
===================
A hand crafted Mirage response may contain variables which are substituted in. For example, a response may contain: ::

    {% set flight_nbr='XX1234' %}
    The flight number is: {{flight_nbr}}

The resulting response served wil be: ::

    The flight number is: XX1234

Code may be used, for example adding random elements to a response. ::

    {% import random %}
    {% set rnd_nbr = random.randint(1,200) %}
    Hello World {{ 1000 + rnd_nbr }}

The resulting response served will be: ::

    Hello World - followed by a number between 1,000 and 1,200.

To put today's date in a response include the following: ::

    {{today_str.format('%d%m%y')}}

Mirage responses are run through a Tornado template and any logic or commands allowed in these templates can be used.
See http://www.tornadoweb.org/en/stable/template.html for details.

Request Data in Responses
=========================

Text Manipulation
-----------------
It is possible to pull data from the stub request and put it in the response. Say you have 200 stubs that are identical apart from a userid. They could be condensed into, one stub which uses the userid from the request in the response.
request: ::

    <userid>abc123</userid>

matcher: ::

    <userid>

response template (using Python): ::

    Hello to {{request_text[8:14]}}

response: ::

    Hello to abc123

XML Manipulation
----------------

Sometimes it is easier to use XPATH to pull data from a request and place it in a response. If you need the SessionId
from this request: ::

    <?xml version="1.0" encoding="UTF-8"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
      xmlns:wbs="http://xml.aaa.com/ws/2009/01/WBS_Session-2.0.xsd">
      <soapenv:Header>
         <wbs:Session>
            <wbs:SessionId>John1234</wbs:SessionId>
                ......

Pull the SessionId from the request and use it within the response template: ::

    {% set namespaces = {'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',  
       'wbs': 'http://xml.aaa.com/ws/2009/01/WBS_Session-2.0.xsd'}%}
    <?xml version="1.0" encoding="UTF-8"?>
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
      xmlns:wbs="http://xml.aaa.com/ws/2009/01/WBS_Session-2.0.xsd">
      <soapenv:Header>
         <wbs:Session>
            <wbs:SessionId>{{xmltree.xpath('//soapenv:Header/wbs:Session/wbs:SessionId', 
                  namespaces=namespaces)[0].text}}</wbs:SessionId>
                ......

Note the xmltree variable is the parsed xml request (as an lxml Root object) made available to the template
if the request is valid xml.

Another example - no namespaces in the request.
Request: ::

    <?xml version="1.0" encoding="UTF-8"?>
    <CompensateCustomersCheck APCWCustom="-1" LocalCurrencyCode="GBP" NumberOfAdults="1">...

Response: ::

    {% set currency_code = xmltree.xpath('/CompensateCustomersCheck')[0].attrib['LocalCurrencyCode'] %}
    <response LocalCurrencyCode={{currency_code}}>pay me</response>

Stateful Stubs
==============
State is important in simulating back-end systems. For example, if one was to check-in passenger Bob on a particular
flight the back-end would allow this request to succeed only one time and subsequent attempts to check-in the same
passenger on the same flight would be rejected. Mirage can emulate this functionality, or if desired for repeatable
tests, Mirage can allow Bob to be checked in multiple times on the same flight.

Stateful stubbing is enabled automatically. If stubs are recorded or loaded in which the same request returns
different responses Mirage will remember this and internally keep track of which response should come next.

If your test is to check-in Bob multiple times, simply do not load the stubs representing the check-in rejection and
Mirage will allow multiple check-ins.

User Exits
==========

Mirage provides hooks into the runtime to execute custom user code. Mirage can execute your custom code 
to transform stub matchers, requests and/or responses. This is a powerful mechanism when your stubs contain 
dynamic data or need to change over time. This can be useful to perform 'intelligent
stubbing' for example to roll dates. The user exit API is contained in the stubo.ext.user_exit module.  

API
---
.. automodule:: stubo.ext.user_exit
   :members:

XML Auto Mangling
-----------------

If your data is XML a convenience class XMLUserExit is provided to enable
auto mangling.

API
---
.. automodule:: stubo.ext.xmlexit
   :members:
   :special-members: __init__, get_exit   
   
.. automodule:: stubo.ext.xmlutils
   :members: 
   :special-members: __init__  
      

Hooks
=====

.. automodule:: stubo.ext.hooks
   :members:
   
.. automodule:: stubo.ext.transformer
   :members: 
   :special-members: __init__  
   
.. automodule:: stubo.model.stub
   :members:         
   
.. automodule:: stubo.model.request
   :members: 
   :special-members: __init__ 

Modules
=======

Modules are added with the put/module command and referenced via the ext_module url arg in the put/stub call.
For example: ::

   put/module?name=/static/cmds/tests/ext/xslt/mangler.py
   delete/stubs?scenario=mangler_xslt
   begin/session?scenario=mangler_xslt&session=mangler_xslt1&mode=record
   put/stub?session=mangler_xslt1&ext_module=mangler, first.request, first.response
   end/session?session=mangler_xslt1

This example dynamically imports a test mangler from the Mirage server. Typically these external python modules
that hook into the Mirage runtime would be sourced from source control system using a URL.

Note:  user exit processing is only enabled if the 'ext_module' variable is set to a pre-loaded module during the
put/stub call. Each Mirage host URL has its own copy of any loaded modules. Such
modules are available to any test and, as such, should typically be loaded once per
test suite.

Splitting
=========

Useful to removing random elements from matchers:
It can happen that the system under test will include seemingly random elements 
in the request. This will cause the next run of the test to not match. This problem 
can be solved by processing matchers when loading - during a record. A matcher 
can be split into two with the variable text left out. Future request must match 
both of the matchers to get the response. An example is: ::

    <Cryptic_GetScreen_Query><Command>FXXNFCDXO/676782009900007706/1214/N1111*12345678:06/P1</Command></Cryptic_GetScreen_Query>

Which becomes two matchers. ::

    <Cryptic_GetScreen_Query><Command>FXXNFCDXO/676782009900007706/1214/N1111*

and ::

    :06/P1</Command></Cryptic_GetScreen_Query>

cutting out the random number '12345678' in the middle. 

This matcher splitting can be done manually or automatically with a user exit.
See /static/cmds/tests/ext/splitters/1/first.commands for and example. It uses the 
rules module at : /static/cmds/tests/ext/aaa.py

Multiple matchers excluding random request elements can be created manually and loaded as such: ::

    put/stub?session=splitter_record, splitter_1.textMatcher, splitter_2.textMatcher, splitter.response


Caching Values
==============
If emulating back-end behaviour means writing some code for a particularly tricky behaviour,
Mirage exposes a simple key-value cache API to matchers and responses.

For example, if a response needs to increment a count each time it is used, you can 
define a module like this ::


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

The lines above to note are: ::

    val = cache.get('foo')

    cache.set('foo', val)

You can set any key and value which is of use.
As with other user extensions the example above can be loaded in a command with: ::

    put/module?name=/static/cmds/tests/ext/cache/example.py
    ....
    put/stub?session=cache_1&ext_module=example&tracking_level=full,1.request,1.response
