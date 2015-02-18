.. undocumented

*********************
Special Features
*********************
Don't use these features unless you know what you are doing !

Force
=====
If you need to delete a scenario and don't care if it has sessions running in
playback or record you can with: ::

    delete/stubs?scenario=abc&force=true

Don't use this in normal stubbing as killing active sessions is poor sportsmanship.
Use and end/session?session=123 instead.

Scenario + Session Concatenation
================================

When accepting a get/response with the session and scenario as HTTP headers Stubo
will concatenate them together: ::
    
    Headers
        ab_stb_scenario: mcw
        ab_stb_session: 1

    Becomes the following:
        session = mcw_1

This has been provided for backwards compatability. Normally a get/response call
only needs the session.

Text Matchers and Responses
===========================

Normally a command file refers to files for the textMatcher and response data.
In most cases this is best as there can be a lot of data. But, one can also
simply enter actual text as follows: ::

    put/stub?session=123,text=some_text, text=some_response_text

This is generally only useful for Stubo demonstrations.
