.. basics

***********
Stub Basics
***********

Stubo simulates back-end systems by matching a request to a response. Request/Response definitions are 'loaded' into Stubo 

Conventions for this documentation:

All Stubo commands are to be prefixed with the server (and port) of the Stubo instance you are using. For example: /stubo/api/get/status would really be 
something like 'http://mystubo/stubo/api/get/status'

Load and Retrieve Stubs
=======================
For the impatient, point your browser at: /stubo/default/exec/cmds?cmdfile=/static/cmds/demo/first.yaml. 
The JSON response from Stubo is meant for machines to read. For a more
human friendly version use the 'back' button on your browser and navigate to the 
'Tracker' page. There you will see the most recent Stubo commands and their 
details. The commands you just ran from first.yaml are: ::

   # First use of Stub-O-Matic
   # run this from a browser with uri:
   #   http://<stubo server>/stubo/default/exec/cmds?cmdfile=/static/cmds/demo/first.yaml
   
   
   # Describe your stubs here       
   recording:
     scenario: first
     session:  first_1
     stubs: 
       - 
        json: {
              "request": {
                  "method": "GET",
                  "bodyPatterns": [
                      {
                        "contains" : ["get my stub"]
                      }
                  ],
              },
              "response": {
                  "status": 200,
                  "body": "Hello {{1+1}} World",
              }
            }
   
   # Provide your requests here          
   playback:
     scenario: first
     session:  first_1
     requests:
       -     
         json: {
                  "method": "GET",
                  "body": "timestamp: 09:23:45
   get my stub",
               }

These will be listed on the Tracker page.
What just happened? The command you made executed a Stub-O-Matic command file (demo/first.yaml). That file loaded a stub into Stubo's database, then simulated a request returning the expected response. These actions were logged and displayed on the Tracker page.

There are a few key concepts that will make stubbing work.

* Scenario - A re-usable set of stubs
* Session - The instance or use of the stubs from a scenario
* Matcher - The matcher used to find the correct response for a request
* Request - A message normally sent to a back-end by the system under test
* Response - A message normally returned by a back-end system
* Stub = Matcher(s), and a response

Stubo commands have been designed to be read, written and used by either humans or the Stubo code. The stub and command files are 
accessed via a URI (http://...). In practice this means putting them into a source code repository such as Subversion (SVN) which you should be doing anyway. 
The file location in the exec/cmds command can be local to Stubo as in the first.yaml example, or (more usual) a URL.

For example you could run: ::

    stubo/default/exec/cmds?cmdfile=https://your-source-code-repo/static/cmds/demo/first.yaml 

Sessions and Scenarios
======================

In order for stubs to be loaded and retrieved in a predictable, automated manner by multiple users many Stubo events 
are controlled by a session. A session is a unit of work that must be started and ended. Sessions have two possible modes of operation:

* record - for loading stubs into the Stubo datastore
* playback - for retrieving stubbed responses during testing

A scenario is a group of stubs that can be used and re-used by multiple sessions.

Recording Stubs
===============

Stubs can be created by hand or auto-recorded from a real system under test.
This is done from what we call a 'Stubo integrator or Stubo client service'. A Stubo integrator is typically a 
custom library that intercepts real system calls and 're-plays' them into a 
Stubo 'recording' via put/stub commands. Java and Python Stubo client libraries are provided 
to help integrate Stubo into your applications. These clients are maintained in github at
https://github.com/Stub-O-Matic/python-client & https://github.com/Stub-O-Matic/java-client.   

If the real system changes its interface, a recording can be repeated to capture the changes.
Of course this requires that the test back-end systems have the correct data in them
to be used successfully.

Stubo provides mechanisms to deal with context sensitive information 
such as transaction ids, dates, user names etc which makes recorded stubs less fragile.
