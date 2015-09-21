.. api

*************
Mirage API v1
*************

The Mirage API v1 returns JSON. The response always returns the version, and payload. The payload
is either contained under 'data' if the response is successful or 'error' for
errors. Errors contain a descriptive message under 'message' and the http error code under 'code'.
Successful responses depend on the call made and are described below.

.. code-block:: javascript
 
    e.g. an error response
    
    {
       "version": "1.2.3", 
       "error": {
           "message": "Session already exists - localhost:first:first_1 in playback mode.", 
           "code": 400
       }
    } 
    
    e.g. a successful response
    
    {
       "version": "1.2.3", 
       "data": {
           "status": "playback", 
           "message": "Playback mode initiated....", 
           "session": "first_1", 
           "scenario": "localhost:first"
       }
    }


exec/cmds
=========

.. code-block:: javascript

    exec/cmds  (GET, POST)
       query args: 
           cmdfile: URL or a file under /static on the mirage server 
            + any user args will be made avaliable to the cmd file template
           session_id: session name to substitute within the cmdfile template, best to prefix this with scenario name if provided (optional) 
       response: shows the list of commands (url, return_code) executed, see the Tracker page for responses      

   Typically command files are used to load stubs into the Mirage db, but you can run any supported commands from a file. 
   
   stubo/api/exec/cmds?cmdfile=/static/cmds/demo/first.commands
   
   {
   "version": "1.2.3", 
   "data": {
      "executed_commands": [
         [
            "delete/stubs?scenario=first", 
            200
         ], 
         [
            "begin/session?scenario=first&session=first_1&mode=record", 
            200
         ], 
         [
            "put/stub?session=first_1,first.textMatcher,first.response", 
            200
         ], 
         [
            "end/session?session=first_1", 
            200
         ], 
         [
            "begin/session?scenario=first&session=first_1&mode=playback", 
            200
         ], 
         [
            "get/response?session=first_1,first.request", 
            200
         ], 
         [
            "end/session?session=first_1", 
            200
         ]
      ], 
      "number_of_requests": 7, 
      "number_of_errors": 0
      }
   }
   
   

   
   stubo/api/exec/cmds?cmdfile=https://your-source-repo/my.commands
   
   Command files can be included in an archive file along with the matcher and response files. You can import your stubs 
   by running the archive file:
   
   stubo/api/exec/cmds?cmdfile=https://your-source-repo/my.zip
   
   Supported archive formats are zip, tar.gz & jar files.

get/version
===========

.. code-block:: javascript

    get/version (GET, POST)

    This call does not touch the db or cache so is useful as a quick 'ping' on the server
    
    stubo/api/get/version
    
    {"version": "1.2.3"}
    
get/status
==========


.. code-block:: javascript

    get/status (GET, POST)  
       query args: 
         scenario=name 
         session=name (session takes precedence)
         check_database=true|false (default true)
         local_cache=true|false (default true)
    
    stubo/api/get/status?scenario=first 
    
    {
    "version": "1.2.3", 
    "data": {
        "cache_server": {
            "status": "ok", 
            "local": true
        }, 
        "info": {
            "cluster": "my-cluster", 
            "graphite_host": "http://my-graphite.com/"
        }, 
        "database_server": {
            "status": "ok"
        }, 
        "sessions": [
            [
                "first_1", 
                "dormant"
            ]
        ]
    }
    
    stubo/api/get/status?session=first_1
    
    {
    "version": "1.2.3", 
    "data": {
        "cache_server": {
            "status": "ok", 
            "local": true
        }, 
        "info": {
            "cluster": "my-cluster", 
            "graphite_host": "http://my-graphite.com/"
        }, 
        "session": {
            "status": "dormant", 
            "system_date": "2014-10-02", 
            "scenario": "localhost:first", 
            "last_used": "2014-10-02 16:00:39", 
            "scenario_id": "542d76a7ac5f73060fc9c2b4", 
            "session": "first_1"
        }, 
        "database_server": {
            "status": "ok"
        }
    }


begin/session
=============

.. code-block:: javascript

    begin/session (GET, POST)  
       query args: 
           scenario = scenario name
           session = session name
           mode = playback|record
           
   stubo/api/begin/session?scenario=first&session=first_1&mode=playback
           
   {
       "version": "5.9.9", 
       "data": {
           "status": "playback", 
           "message": "Playback mode initiated....", 
           "session": "first_1", 
           "scenario": "localhost:first"
       }
   }
   
   Note on duplicate scenarios and sessions:

   * A scenario name prefixed with the mirage host name must be unique. One cannot record a new scenario with a duplicate host + scenario name.
   * Sessions are instances of scenario's stubs and must be unique within a host.
   * Sessions can not be deleted if in playback or record mode
   * Scenarios can not be deleted if any session based on it is in playback or record mode.

end/session
===========

.. code-block:: javascript

    end/session (GET, POST)  
       query args:
           session: session name 
    
    stubo/api/end/session?session=first_1 
    
    {
       "version": "1.2.3", 
       "data": {
           "message": "Session ended"
       }
    }

    * Ending a session which does not exist is OK and will complete successfully

end/sessions
============

.. code-block:: javascript

    end/sessions (GET, POST)  
       query args:
           scenario: scenario name 
    
    stubo/api/end/sessions?scenario=first 
    
    {
        "version": "6.1.3", 
        "data": {
            "first_1": {
                "message": "Session ended"
            }, 
            "first_2": {
                "message": "Session ended"
            }
        }
    }


put/scenarios
=============

Scenario names can be changed by providing current scenario name and new name. This operation includes renaming all the
stubs that belong to this scenario, as well as changing scenario name value in saved sessions. Sessions will be
transfered to new scenario. During rename procedure - all sessions will be set to dormant mode. Returns status code
412 if no name or no query is provided. Returns status code 400 if scenario name has illegal characters.
Scenario name check regex: r'[\w-]*$' - letters, numbers, dashes, underscores

.. code-block:: javascript

    put/scenarios/(?P<scenario_name>[^\/]+) (GET)
       query args:
           new_name: new scenario name

    stubo/api/put/scenarios/first?new_name=new_first_scenario_name

    {
    "Scenarios changed": 1,

    "Remapped sessions": [
             {
                 "name": "myscenario_session2"
             }
         ],
    "New name": "localhost:new_first_scenario_name",
    "Old name": "localhost:first",
    "Stubs changed": 5,
    "Pre stubs changed": 0
    }


put/stub
========

.. code-block:: javascript

    put/stub (POST)  
       query args: 
            session = session name
            ext_module = external module name without .py extenstion (optional)
            delay_policy =  delay policy name (optional)
            stateful = treat duplicate stubs as stateful otherwise ignore duplicates if stateful=false (default true, optional)
            tracking_level: full or normal (optional, overrides host or global setting) 
            + any user args will be made avaliable to the matcher & response templates and any user exit code
    e.g. 
    stubo/api/put/stub?session=my_session
    
    given request=<status>IS_OK</status> & response=<response>YES</response>
    JSON POST data
    {
        "request": {
            "method": "POST",
            "bodyPatterns": [
                { "contains": ["<status>IS_OK</status>"] }
            ]
            },
        "response": {
            "status": 200,
            "body": "<response>YES</response>"
        }
    }   
    returns
    {
       "data": {
           "message": "put 54378c0dac5f7302b5cb8e56 stub"
       }, 
       "version": "1.2.3"
    }    
    
    Treatment of duplicate stubs:

   * If both the request and the response already exist for the scenario in record mode, then the stub will not be created.
   * If the request exists, but with a different response, the second response will be recorded and the stub becomes a 'stateful stub'.
   * Duplicate stubs can exist in different scenarios

Notes:

see :ref:`stub_reference` for stub definitions.    
see :ref:`daterolling` for an example of using user arguments to perform date rolling  


get/stublist
============

.. code-block:: javascript

    get/stublist (GET, POST)  
       query args: 
           scenario: scenario name
           host: host uri to use (defaults to host used in request uri, optional)
          
    stubo/api/get/stublist?scenario=first
    
   {
    "version": "1.2.3", 
    "data": {
        "stubs": [
            {
                "recorded": "2014-10-10", 
                "args": {
                    "session": "first_1"
                }, 
                "request": {
                    "bodyPatterns": [
                        {
                            "contains": [
                                "get my stub\n"
                            ]
                        }
                    ], 
                    "method": "POST"
                }, 
                "response": {
                    "status": 200, 
                    "body": "Hello {{1+1}} World\n"
                }
            }
        ], 
        "scenario": "first"
    }
   


put/delay_policy
================

.. code-block:: javascript

    put/delay_policy (GET, POST)  
       query args: 
           name: delay name
           delay_type: fixed, normalvariate or weighted
           milliseconds: used with fixed delay_type only
           mean: used with normalvariate delay_type only
           stddev: used with normalvariate delay_type only
           values: used with weighted delay_type only. values is a delimited string of delays. 
           For each delay the last value represents the percentage this delay will occur. 
    
    stubo/api/put/delay_policy?name=slow&delay_type=fixed&milliseconds=1000     
    
    {
       "version": "1.2.3", 
       "data": {
           "status": "new", 
           "message": "Put Delay Policy Finished", 
           "delay_type": "fixed", 
           "name": "slow"
       }
    }
    
    i.e. to set a weighted percentage of delays with 5% fixed at 30s, 15% having a delay of 5s +/- 1s and 70% having a delay of 1s +/- 0.5s 
    stubo/api/put/delay_policy?name=pcent_random_samples&delay_type=weighted&delays=fixed,30000,5:normalvariate,5000,1000,15:normalvariate,1000,500,70

    {
       "version": "1.2.3", 
       "data": {
           "status": "new", 
           "message": "Put Delay Policy Finished", 
           "delay_type": "weighted", 
           "name": "pcent_random_samples"
       }
    }

get/delay_policy
================

.. code-block:: javascript

    get/delay_policy (GET, POST)  
       query args: 
           name: delay name (optional lists all if not provided)
    
    stubo/api/get/delay_policy?name=slow       
    {
       "version": "1.2.3", 
       "data": {
           "slow": {
               "delay_type": "fixed", 
               "name": "slow", 
               "milliseconds": "1000"
           }
       }
    }
           


delete/delay_policy
===================

.. code-block:: javascript

    delete/delay_policy (GET, POST)  
       query args: 
           name: delay name (optional deletes all if not provided)
    
    stubo/api/delete/delay_policy?name=slow  
        
    {
       "version": "1.2.3", 
       "data": {
           "message": "Deleted 1 delay policies from [u'slow']"
       }
    }
     


get/response
============

.. code-block:: javascript

    get/response (POST)  
       query args: 
           session: session name
           tracking_level: full or normal (optional, overrides host or global setting) 
       POST data: request payload
       HTTP headers:
         Mirage-Request-Session=123 Optional, can be used in place of session on the URL.
       returns stub response payload in HTTP body if ok
       on error returns mirage json error response  
           
    stubo/api/get/response?session=first_1 
    POST data: get my stub
    returns: Hello 2 World
    




delete/stubs
============

Stubs should be mastered in a code repository such as SVN. Delete/stubs will remove stubs from the Mirage database. This should be run at the end of each test run.

.. code-block:: javascript

    delete/stubs (GET, POST)  
       query args:
           scenario: scenario name
           host: host uri to use (defaults to host used in request uri, optional)
           force: false or true (optional, defaults to false) 
   
   stubo/api/delete/stubs?scenario=first
           
   {
       "version": "1.2.3", 
       "data": {
           "scenarios": [
               "localhost:first"
           ], 
           "message": "stubs deleted."
       }
   }
           
   * All sessions must be in a dormant state to delete the stubs unless force=true is used
   * Deleting a scenario that does not exist is OK and will complete successfully

get/export
==========

Export a recorded scenario. To support repeatable testing a recording should be exported with get/export and the resulting archive file saved to your source code repository (GIT etc).
The exported archive contains all scenario stubs and a command script to reload them. The get/export call also supports exporting 'runnable' scenarios. A 'runnable' scenario will add
a playback of a previous session to the command script. This can be useful to compare different test runs with each other.

.. code-block:: javascript

    get/export (GET, POST)  
       query args:
           scenario: scenario name
           session_id: session id to use within the export (optional, defaults to epoch time)
           export_dir: export dir name (optional, defaults to scenario key)
           runnable: create a runnable scenario of a previous playback (optional)
           playback_session: playback session to use (required with runnable)
           session_id: session name to substitute within the cmdfile template (optional)
    returns links to exported archive files (*.zip, *.tar.gz, *.jar)
           
    stubo/api/get/export?scenario=first       
           
    {
       "version": "1.2.3", 
       "data": {
           "scenario": "first", 
           "export_dir_name": "/Users/rowan/dev/eclipse/workspace/stubo/static/exports/localhost_first", 
           "links": [
               [
                   "first_1412947560_0.response.0", 
                   "http://Rowan-MacBook-Pro-5.local:8001/static/exports/localhost_first/first_1412947560_0.response.0?v=1d63737c9cdb7b1433d76b52661c9db9"
               ], 
               [
                   "first_1412947560_0_0.textMatcher", 
                   "http://Rowan-MacBook-Pro-5.local:8001/static/exports/localhost_first/first_1412947560_0_0.textMatcher?v=088c16fa5004e2467126cfeaf8da3cd3"
               ], 
               [
                   "first.commands", 
                   "http://Rowan-MacBook-Pro-5.local:8001/static/exports/localhost_first/first.commands?v=d56a304dddafe558ccfe9340ebdb41e8"
               ], 
               [
                   "first.zip", 
                   "http://Rowan-MacBook-Pro-5.local:8001/static/exports/localhost_first/first.zip?v=34c1c698d09e7e3f1a3a10a2834bbbd6"
               ], 
               [
                   "first.tar.gz", 
                   "http://Rowan-MacBook-Pro-5.local:8001/static/exports/localhost_first/first.tar.gz?v=8e5ac69d3041941aa4cc5dfdee41326b"
               ], 
               [
                   "first.jar", 
                   "http://Rowan-MacBook-Pro-5.local:8001/static/exports/localhost_first/first.jar?v=34c1c698d09e7e3f1a3a10a2834bbbd6"
               ]
           ]
       }
    }
    
    & runnable export
    
    stubo/api/get/export?scenario=first&runnable=true&playback_session=first_1
    
    {
        "version": "1.2.3", 
        "data": {
            "runnable": {
                "last_used": {
                    "start_time": "2015-03-24 16:57:03.248000+00:00", 
                    "remote_ip": "::1"
                }, 
                "playback_session": "first_1", 
                "number_of_playback_requests": 1
            }, 
            "scenario": "first", 
            "links": [
                [
                    "first_1427285580_0.response.0", 
                    "http://vuze-on-pc2.home:8001/static/exports/localhost_first/first_1427285580_0.response.0?v=1d63737c9cdb7b1433d76b52661c9db9"
                ], 
                [
                    "first_1427285580_0_0.textMatcher", 
                    "http://vuze-on-pc2.home:8001/static/exports/localhost_first/first_1427285580_0_0.textMatcher?v=088c16fa5004e2467126cfeaf8da3cd3"
                ], 
                [
                    "first_1427285580_0.request", 
                    "http://vuze-on-pc2.home:8001/static/exports/localhost_first/first_1427285580_0.request?v=925721a672115ec9bfc24f55a6979a63"
                ], 
                [
                    "first.commands", 
                    "http://vuze-on-pc2.home:8001/static/exports/localhost_first/first.commands?v=98ad4927b82478744dfa004f48f88aff"
                ], 
                [
                    "first.zip", 
                    "http://vuze-on-pc2.home:8001/static/exports/localhost_first/first.zip?v=66a370b25ca2065abc4deb347ee77ce6"
                ], 
                [
                    "first.tar.gz", 
                    "http://vuze-on-pc2.home:8001/static/exports/localhost_first/first.tar.gz?v=da76a1ce23a9cfe2dc1895955021f3c4"
                ], 
                [
                    "first.jar", 
                    "http://vuze-on-pc2.home:8001/static/exports/localhost_first/first.jar?v=66a370b25ca2065abc4deb347ee77ce6"
                ]
            ], 
            "export_dir_path": "/Users/rowan/dev/eclipse/workspace/opencredo/stubo/latest/stubo-app/stubo/static/exports/localhost_first"
        }
    }
    
    
           

get/stubcount
=============

.. code-block:: javascript

    get/stubcount (GET, POST)  
       query args:
           scenario: scenario name (optional)

    Returns the number of stubs for a given scenario or all scenarios on host if
    the scenario is not provided.
    
    stubo/api/get/stubcount?scenario=first
    
    {
       "version": "1.2.3", 
       "data": {
           "count": 1, 
           "scenario": "first"
       }
    }


put/module
==========

User exits can be applied to perform custom manipulation of Mirage matchers and responses.
The user exits are python code defined with the UserExit API. The code is input 
into mirage with the following API call.


.. code-block:: javascript

    put/module (GET, POST)  
       query args:
           name: full path to module can be a uri 
    
    stubo/api/put/module?name=/static/cmds/tests/ext/xslt/mangler.py
           
    {
       "version": "1.2.3", 
       "data": {
           "message": "added modules: ['localhost_mangler_v1']"
       }
    }       
       
Notes:

If the module code has not changed an error is returned indicating that the source has not changed otherwise 
a new version of the module is added to mirage dynamically.

get/modulelist
==============

.. code-block:: javascript

    get/modulelist (GET, POST)  
    returns list of loaded modules       
    
    stubo/api/get/modulelist
           
    {
       "version": "1.2.3", 
       "data": {
           "info": {
               "mangler": {
                   "loaded_sys_versions": [
                       "localhost_mangler_v1"
                   ], 
                   "latest_code_version": 1
               }
           }, 
           "message": "list modules"
       }
    }       


delete/module
=============

Delete named module.

.. code-block:: javascript

    delete/module (GET, POST)  
       query args:
           name: name of module without .py ext 

   {
       "version": "1.2.3", 
       "data": {
           "deleted": [
               "localhost:mangler"
           ], 
           "message": "delete modules: [u'mangler']"
       }
   }

delete/modules
==============

Delete all modules from this host URL.

.. code-block:: javascript

    delete/modules (GET, POST)  
           
    {
        "version": "6.1.3", 
        "data": {
            "deleted": [
                "localhost:strip_ns", 
                "localhost:ignore_dates", 
            ], 
            "message": "delete modules: ['strip_ns', 'ignore_dates']"
        }
    }       
           
Set Tracking Level
==================
All API calls to Mirage will result in a tracking record being created. Default level tracking includes:

* start time
* duration
* any user configured delay
* mirage function
* return code and data
* session and scenario names
* response size
* server (Mirage server that handled the request)
* host (DNS of mirage used on the request)
* remote_ip (IP address of the client)

In addition, get/response calls can optionally force other items to be tracked including:

* matchers used
* matcher text before, during and after any mangling
* response text before, during and after any mangling

To enable/disable logging.

.. code-block:: javascript

    put/setting (GET, POST)  
       query args:
           tracking_level=full or normal
    
    stubo/api/put/setting?setting=tracking_level&value=full       
    {
       "version": "1.2.3", 
       "data": {
           "new": "false", 
           "host": "localhost", 
           "all": false, 
           "tracking_level": "full"
       }
    }       


Click on a get/response item in the Tracker page to see the full tracking data.

Blacklist a host URL
====================

To stop a virtual mirage host being used perform the following:

.. code-block:: javascript

    stubo/api/put/setting?host=roguehost&setting=blacklisted&value=on
    
    {
       "version": "1.2.3", 
       "data": {
           "blacklisted": "on", 
           "new": "true", 
           "host": "roguehost", 
           "all": 0
       }
    }
    
   stubo/api/get/setting?host=roguehost&setting=blacklisted
    
   {
       "version": "1.2.3", 
       "data": {
           "blacklisted": "on", 
           "all": 0, 
           "host": "roguehost"
       }
   }
   
   Users will not be able to start a session with this host after it has been 'blacklisted'.
   
   roguehost/stubo/api/begin/session?...
   
   {
       "version": "1.2.3", 
       "error": {
           "message": "Sorry the host URL 'roguehost' has been blacklisted. Please contact Mirage support.", 
           "code": 400
       }
   }


Create Bookmark
===============

This is usually done via the GUI.

+---------------+--------------------------------------------------------------------+
| Method        | POST put/bookmark?name=abc&session=bob&session=mary&response=12345 |
+---------------+--------------------------------------------------------------------+
| URL Variables | name=bookmark_name                                                 |
|               | session=session_1&session=session_2                                |
|               | response=1234 (response key)                                       |
+---------------+--------------------------------------------------------------------+
| Request Body  | -empty-                                                            |
+---------------+--------------------------------------------------------------------+
| Returns       |                                                                    |
+---------------+--------------------------------------------------------------------+

Jump to Bookmark
================

+---------------+--------------------------------------------------------------------------------+
| Method        | GET jump/bookmark                                                              |
+---------------+--------------------------------------------------------------------------------+
| URL Variables | name=bookmark_name                                                             |
|               | session=session_1&session=session_2                                            |
+---------------+--------------------------------------------------------------------------------+
| Request Body  | -empty-                                                                        |
+---------------+--------------------------------------------------------------------------------+
| Returns       | {"version": "5.5.0", "data": {"results": [["e121bef2c162a2ee4ae63", "2", 0]]}} |
+---------------+--------------------------------------------------------------------------------+

Delete Bookmark
===============

+---------------+--------------------------------------------------------------------------------+
| Method        | GET delete/bookmark                                                            |
+---------------+--------------------------------------------------------------------------------+
| URL Variables | name=bookmark_name                                                             |
|               | scenario=abc                                                                   |
+---------------+--------------------------------------------------------------------------------+
| Request Body  | -empty-                                                                        |
+---------------+--------------------------------------------------------------------------------+
| Returns       | {"version": "5.5.0", "data": {"bookmark": "bob_leads", "deleted": 0}}2", 0]]}} |
+---------------+--------------------------------------------------------------------------------+

List Bookmarks
==============

+---------------+---------------------------------------------------------------------+
| Method        | GET get/bookmark                                                    |
+---------------+---------------------------------------------------------------------+
| URL Variables | name=bookmark_name (optionl, lists all if absent)                   |
+---------------+---------------------------------------------------------------------+
| Request Body  | -empty-                                                             |
+---------------+---------------------------------------------------------------------+
| Returns       | {"version": "5.5.0", "data": {"trng": {"bob_leads": {"e1213": "1"}, |
|               | "ted_leads": {"e1213b": "2"}}}}                                     |
+---------------+---------------------------------------------------------------------+

get/stats
=========

Obtain the percent of get/response calls that are above a given latency value. 

.. code-block:: javascript

    get/stats (GET, POST)  
       query args:
           percent_above_value = threshold value in millisecs
           from=start time of metrics 
       
    e.g. to find the percent of Mirage responses that take more than 40ms (during the past 30min)  

    /stubo/api/get/stats?percent_above_value=40&from=-30mins 
    
    {
       "version": "5.6.2", 
       "data": {
           "from": "-30mins", 
           "target": "averageSeries(stats.timers.stubo.aws_cluster1.*.stuboapi.get_response.latency.mean_90)", 
           "metric": "latency", 
           "to": "now", 
           "percent_above_value": 40, 
           "pcent": 0.0
       }
    }

    The key value being "pcent" which in this case is 0.0.
