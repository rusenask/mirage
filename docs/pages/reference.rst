.. reference

*********
Reference
*********

.. _stub_reference:

Stub Definition
===============

A stub definition consists of a request, response pair. The JSON definition 
is as follows:

.. code-block:: javascript

 {
        "request": {
            "method": "GET|POST|PUT|DELETE",
            "bodyPatterns": [
                { "contains": ["<status>OK</status>"] }
            ],
            "urlPath": "/get/me",
            "queryArgs": {
                "find" : "me",
                "when" : "now"
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
      

