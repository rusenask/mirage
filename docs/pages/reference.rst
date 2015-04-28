.. reference

*********
Reference
*********

.. _stub_reference:

Stub Definition
===============

A stub definition consists of a request, response pair. The JSON definition 
is as follows:

Note this example show the full set of matching criteria. In reality some 
matchers would not be combined, e.g. xpath and jsonpath

.. code-block:: javascript

 {
        "request": {
            "method": "GET|POST|PUT|DELETE",
            "bodyPatterns": [
                { 
                  "contains" : ["<status>OK</status>"],
                  "xpath"    : ["/bookstore/book[price>35.00]", 
                                ("//find/me", {"user" : "http://www.my.com/userschema", 
                                               "info" : "http://www.my.com/infoschema"})],
                  "jsonpath" : ["bookstore.book"] 
                }
            ],
            "urlPath": "/get/me",
            "urlPattern" : "/get/me[0-9]+",
            "queryArgs": {
                "find" : "me",
                "when" : "now"
            },
            "headers" : {
               "Content-Type" : "text/xml",
               "X-Custom-Header" : "1234"
            }
        },
        "response": {
            "status": 200,
            "body": "<response>YES</response>"
        }
 }

Most leaf keys can be negated by adding a '!' prefix to the key

e.g.

.. code-block:: javascript

    {
    
       "request": {
          "!method" : "GET"
          ...
       }
    }
      

