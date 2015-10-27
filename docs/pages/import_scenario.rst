.. import_scenario

Scenario Importing
******************

Configuration files are used to load stub files and add behaviour to them (state, dates, etc.). These configuration files
must obey .yaml syntax so libraries that were designed to load .yaml will always be able to modify them on the fly.

Stubs can also be loaded and tested using individual calls to the Mirage server
using the Mirage HTTP API. Configuration files are a shorthand for the API, making it simpler
to enable repeatable, automated interactions with Mirage by directly uploading scenario and setting it to playback mode
for a particular test. All scenarios (with stubs that belong to them have to be archived into one zip file. Mirage will
then find .yaml configuration file and based on it will create scenario object and session. It will treat every ".json"
file found in the archive as a separate stub.


Configuration file (YAML)
=========================

An example ::

   # Mirage YAML
     
   # Describe your stubs here       
   recording:
     scenario: rest
     session:  rest_recording


Below is an example of stub json file.

stub1.json ::

   {
          "request": {
              "method": "GET",
              "bodyPatterns": {
                 "contains": [
                    "0"
                 ]
              },
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
              "bodyPatterns": {
                 "contains": [
                    "1"
                 ]
              },
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

Note that these json payloads for the request and response are defined as strings.


