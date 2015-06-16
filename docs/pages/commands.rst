.. commands

Stubo Command File
******************

Command files are used to load stub files and add behaviour to them (state, dates, etc.).

Stubs can also be loaded and tested using individual calls to the Stub-O-Matic server
using the Stubo HTTP API. Command files are a shorthand for the API, making it simpler 
to enable repeatable, automated interactions with Stub-O-Matic by grouping a set of commands together required for a particular test.


Command file (YAML)
===================

An example ::

   # Stubo YAML
   # Execution ordering is 1) commands, 2) recording 3) playback
   
   # Commands go here 
   commands:
     -
       put/module:
         vars:
           name: /static/cmds/tests/rest/yaml/noop.py 
     -  
       put/delay_policy:
         vars:
           name: slow
           delay_type: fixed
           milliseconds: 1000 
     
   # Describe your stubs here       
   recording:
     scenario: rest
     session:  rest_recording
     stubs: 
       - 
        file: stub1.json
        vars:
           recorded_at : "{{as_date('2015-01-10')}}" 
           ext_module : noop
       - 
        json: {
              "request": {
                  "method": "GET",
                  "bodyPatterns": [
                      {
                        "jsonpath" : ["cmd.x"]
                      }
                  ],
                  "headers" : {
                     "Content-Type" : "application/json",
                     "X-Custom-Header" : "1234"
                  }
              },
              "response": {
                  "status": 200,
                  "body": "{\"version\": \"1.2.3\", \"data\": {\"status\": \"all ok 2\"}}",
                   "headers" : {
                     "Content-Type" : "application/json",
                     "X-Custom-Header" : "1234"
                  }
              }
            }
        vars:
           foo: bar
   
   # Provide your requests here          
   playback:
     scenario: rest
     session:  rest_playback
     requests:
       -
         file: request1.json
         vars:
            played_at: "{{as_date('2015-01-20')}}"
       -     
         json: {
                  "method": "GET",
                  "body": {"cmd": {"x": "y"}},
                  "headers" : {
                     "Content-Type" : "application/json",
                     "X-Custom-Header" : "1234"
                  }
               }
         vars:
            played_at: "{{as_date('2015-01-20')}}"
            
Note the payloads can be defined either in place with the 'json' key or point to an external reference via
the 'file' key. The file can either reference a local statically served file as shown above or be a URI reference. 
Typically it will be a URI reference to a location in a users source control system where their stubs are stored.

The local file references in this example are shown below

stub1.json ::

   {
          "request": {
              "method": "GET",
              "bodyPatterns": [
                  {
                    "jsonpath" : ["cmd.a"]
                  }
              ],
              "headers" : {
                 "Content-Type" : "application/json",
                 "X-Custom-Header" : "1234"
              }
          },
          "response": {
              "status": 200,
              "body": "{\"version\": \"1.2.3\", \"data\": {\"status\": \"all ok\"}}",
               "headers" : {
                 "Content-Type" : "application/json",
                 "X-Custom-Header" : "1234"
              }
          }
   }
   
request1.json ::

   {
          "request": {
              "method": "GET",
              "bodyPatterns": [
                  {
                    "jsonpath" : ["cmd.a"]
                  }
              ],
              "headers" : {
                 "Content-Type" : "application/json",
                 "X-Custom-Header" : "1234"
              }
          },
          "response": {
              "status": 200,
              "body": "{\"version\": \"1.2.3\", \"data\": {\"status\": \"all ok\"}}",
               "headers" : {
                 "Content-Type" : "application/json",
                 "X-Custom-Header" : "1234"
              }
          }
   }   

Note that these json payloads for the request and response are defined as strings. Stubo also excepts the defintion as dictionaries.
            
         
Command Scripting
=================

The YAML file is run through a tornado templete processor before beging parsed and executed by Stubo. Any variables defined such
as 'played_at' will evaluated and appropriate subsitutions made.

A roll date example 

(dateroll.yaml) ::

   playback:
     requests:
     - file: dateroll_1433930288_0.request
       response: dateroll_1433930288_0.stubo_response
       vars:
         getresponse_arg: this stub was played at 2015-06-10 09:57:44.839438
         play_date: '2014-09-12'
         priority: '1'
         putstub_arg: this stub was recorded at 2015-06-10 09:57:44.839387
         rec_date: '2014-09-10'
         tracking_level: full
     scenario: dateroll
     session: dateroll_1433930288
   recording:
     scenario: dateroll
     session: dateroll_1433930288
     stubs:
     - file: dateroll_1433930288_0.json
     
Referenced files 

dateroll_1433930288_0.json ::

   {
      "priority": 1, 
      "args": {
         "priority": "1", 
         "rec_date": "2014-09-10", 
         "putstub_arg": "this stub was recorded at 2015-06-10 09:57:44.839387"
      }, 
      "request": {
         "bodyPatterns": {
            "contains": [
               "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\" ?>\n<rollme>                        \n   <OriginDateTime>{{roll_date(\"2014-09-10\", as_date(rec_date), as_date(play_date))}}T00:00:00Z</OriginDateTime>\n</rollme>"
            ]
         }, 
         "method": "POST"
      }, 
      "response": {
         "body": "<response>\n<putstub_arg>{% raw putstub_arg %}</putstub_arg>\n<getresponse_arg>{{ getresponse_arg }}</getresponse_arg>\n</response>", 
         "status": 200
      }
   } 
   
dateroll_1433930288_0.request ::
   
   {
   "body": "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<rollme>\n    <OriginDateTime>2014-09-12T00:00:00Z</OriginDateTime>\n</rollme>", 
   "headers": "{}", 
   "host": null, 
   "path": null, 
   "query": "", 
   "uri": null, 
   "method": "POST"
   }  
   
     

