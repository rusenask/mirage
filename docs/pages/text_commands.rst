.. text_commands

Mirage Command File (text format)
*********************************

The line orientated text version of the command file is an old format. It does
not support the matching required for REST. For example, you can't match on the 
request headers or method. It only supports one type of matcher which is the
'body contains' matcher. If the text specified for the 'body contains' matcher stub is
found in the request a match is found. This is often however the only type of
matcher required to successfully  stub a system. This format is still supported
for import via exec/cmds but will *not* be exported anymore. If a text commands
file is imported via a '.commands' text file on export via get/export a '.yaml'
file will be exported. 

Text Command file
=================

* Lines beginning with a '#' are treated as comments
* Commands follow the Mirage REST API, for example: begin/session?scenario=abc&session=12345&mode=record
* When the API requires something in the HTTP body, input can be sourced by listing files after the command (separated by commas). Files are assumed to be in the same directory as the command file. Alternatively a full URI can be provided to source the input (matcher, request or response).
* Blank lines are ignored.
* An example command is: put/stub?session=12345',feng_001.textMatcher, feng_002.textMatcher, feng_001.response. A put/stub command must have at least one matcher file and one response file. This example has two matchers.

What goes in the command files?

* A .textMatcher file could be some or all of the text from the request, e.g. AB1234</FlightInfoQuery>
* Multiple .textMatchers files may be used in a stub. All must evaluate to True against the request for a response to be returned.
* .request files contain the text of a request (e.g. text, xml, json). Note the using playback in commands is only used to test the stubs as these would be issued by the real system being tested in normal situations.
* .response files contain the text of a response (e.g. text, xml, json).
* Any naming convention can be used for matcher, request and response files. 
  We have used suffixes of .textMatcher, .request & .response but you are free to use other extensions like matcher.xml, request.json, response.xml etc.

Command Scripting
=================
Mirage supports the ability to load stubs from various and multiple sources. This means people can organise all the stubs that support a particular service or 
use case together, and any test that needs those stubs could pull them in from common stub libraries maximising stub reuse. ::

    {% set foreign_url = 'http://www.google.co.uk' %}
    {% set other_url = 'http://www.sun.com' %}
    delete/stubs?scenario=smart
    begin/session?scenario=smart&session=smart_1&mode=record
    put/stub?session=smart_1,url={{other_url}},url={{foreign_url}}
    put/stub?session=smart_1,text=random_rubble,text=response_text
    end/session?session=smart_1

Command files are also programmable with Python code snippets. See the example below: ::

    {% set session_name = 'smart_1' %}
    delete/stubs?scenario=smart
    begin/session?scenario=smart&session={{session_name}}&mode=record
    put/stub?session={{session_name}},first.textMatcher,first.response
    end/session?session={{session_name}}
    begin/session?scenario=smart&session={{session_name}}&mode=playback
    # make 3 requests
    {% for i in range(0,3) %}
    get/response?session={{session_name}},first.request
    {% end %}
    end/session?session={{session_name}}

Passing Arguments
=================
Arguments can be passed into command files and used in them. The following example
allows the session and scenario to be named externally to the command file. ::

    exec/cmds?cmdFile=/static/cmds/tests/accept/smart_arg.commands&scen=bob&session=smart_1

The above call can be used as follows: ::

    delete/stubs?scenario={{scen[0]}}
    begin/session?scenario={{scen[0]}}&session={{ session[0] }}&mode=record
    put/stub?session={{session[0]}},first.textMatcher,first.response
    end/session?session={{session[0]}}
    begin/session?scenario={{scen[0]}}&session={{session[0]}}&mode=playback
    {% for i in range(0,3) %}
    get/response?session={{session[0]}},first.request
    {% end %}
    end/session?session={{session[0]}}

