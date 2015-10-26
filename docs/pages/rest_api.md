# REST API v2

Mirage REST API v2 returns JSON. The response always returns the version, and payload. Responses are similar to
v1 API responses. The payload is either contained under 'data' if the response is successful or 'error' for
errors. Errors contain a descriptive message under 'message' and the http error code under 'code'.
Successful responses depend on the call made and are described below.

Encoding "application/json"

## Create scenario object

Creates scenario object. Client must specify scenario name in the request body.

* __URL__: /stubo/api/v2/scenarios
* __Method__: PUT
* __Response codes__:
   + __201__ - scenario created
   + __422__ - scenario with that name already exists
   + __400__ - something is missing (e.g. name)
* __Example request body__:
```javascript
{
  "scenario": "scenario_name"
}
```

## Upload scenario with session & stubs

You can upload existing scenarios directly into Mirage via this API call. Currently it only accepts .zip format and only
.yaml configuration file.

* __URL__: /api/v2/scenarios/upload
* __Method__: POST
* __Encoding__: "multipart/form-data"
* __Response codes__:
   + __200__ - Scenario uploaded successfully.
   + __415__ - Content type not supported (format not accepted).
   + __400__ - Configuration file found, however failed to read it.
   + __422__ - Scenario already exists.

Example scenario_x.zip content structure:

```
scenario_x.yaml
stub_0.json
stub_1.json
stub_2.json
stub_3.json
stub_4.json
```

As you can see - everything is expected to be in the same directory, no inner directory structure is expected.

Defining .yaml configuration:

```
recording:
  scenario: scenario_x
  session: session_x
```

Note that by default Mirage exported yaml file looks like this:

```
recording:
  scenario: scenario_x
  session: session_x
  stubs:
  - file: stub_0.json
  - file: stub_1.json
  - file: stub_2.json
  - file: stub_3.json
  - file: stub_4.json
```

Although, during upload it ignores "stubs" key and treats every .json file in the archived zip as a separate stub.

When Mirage finds yaml configuration - it gets scenario name and creates it.
After that - reads every file from the archive that ends with ".json".
After all the stubs were added to the database -
starts a session in playback mode. Scenario is then ready for testing.

Example stub .json structure:
```
{
   "priority": 9903,
   "args": {
      "priority": "9903"
   },
   "request": {
      "bodyPatterns": {
         "contains": [
            "<tag> matcher here </tag>"
         ]
      },  
      "method": "POST"
   },
   "response": {
      "body": "<response> Response here </response>\n",
      "headers":
      "status": 200
   }
}
```

### Example upload (Python)

Below is an example pseudocode for uploading files to Mirage:

```
def upload(file_name, mirage_uri):
    """
    file_name - path to zip archive.
    mirage_uri - full Mirage URL (http://miragehostname:8001)
    """
    # reading file
    with open(file_name, 'r') as stream:
        # preparing data
        files = [('files', (file_name, stream, 'application/zip'))]
        data = {}

        resp = requests.post(mirage_uri + "/api/v2/scenarios/upload",
                             files=files, data=data)
        if resp.status_code == 200:
            print("Upload success!")
    return
```

You can upload multiple archives at once. Every archive should be self contained - 
yaml configuration and stubs archived together.

## Get scenario list

Returns a list of scenarios with their name and scenarioRef attributes. This attribute
can the be used to get scenario details (sessions, stubs, size, etc...). Your
application can look for these keys and use them to directly access resource
instead of generating URL on client side.

* __URL__: /stubo/api/v2/scenarios
* __Method__: GET
* __Response codes__:
   + __200__ - scenario list returned
* __Example output__:
```javascript
{
  "data": [
    {"scenarioRef": "/stubo/api/v2/scenarios/objects/localhost:scenario_1",
    "name": "localhost:scenario_1"},
    {"scenarioRef": "/stubo/api/v2/scenarios/objects/localhost:scenario_10",
     "name": "localhost:scenario_10"},
     ...,
     ...,
     ]
}
```
## Get scenario list with details

Returns a list of scenarios with details.

* __URL__: /stubo/api/v2/scenarios/detail
* __Method__: GET
* __Response codes__:
   + __200__ - scenario list with details returned
* __Example output__:
```javascript
{
  "data": [
  {
    "space_used_kb": 0,
    "name": "localhost:scenario_1",
    "sessions": [],
    "scenarioRef": "/stubo/api/v2/scenarios/objects/localhost:scenario_1",
    "recorded": "-",
    "stub_count": 0},
  {
    "space_used_kb": 544,
    "name": "localhost:scenario_10",
    "sessions": [
        {
          "status": "playback",
          "loaded": "2015-07-20",
          "name": "playback_10",
          "last_used": "2015-07-20 13:09:05"}
        ],
     "scenarioRef": "/stubo/api/v2/scenarios/objects/localhost:scenario_10",
     "recorded": "2015-07-20",
     "stub_count": 20},
     ...,
     ...,
   ]
}
```

## Get scenario details

Returns specified scenario details. Scenario name can be provided with a host,
for example stubo_c1.yourcorporateaddress.com:scenario_name_x

* __URL__: /stubo/api/v2/scenarios/objects/<scenario_name>
* __Method__: GET
* __Response codes__:
   + __200__ - specified scenario details
   + __404__ - specified scenario not found
* __Example output__:
```javascript
{
  "space_used_kb": 697,
  "name": "localhost:scenario_13",
  "sessions": [
    {"status": "playback",
    "loaded": "2015-07-20",
    "name": "playback_13",
     "last_used": "2015-07-20 13:09:05"}
   ],
   "stubs": 26,
   "recorded": "2015-07-20",
   "scenarioRef": "/stubo/api/v2/scenarios/objects/localhost:scenario_13"
 }
```

## Delete scenario

Deletes scenario object and removed it's stubs from cache.

* __URL__: /stubo/api/v2/scenarios/objects/<scenario_name>
* __Method__: DELETE
* __Response codes__:
   + __200__ - scenario deleted
   + __412__ - precondition failed - specified scenario does not exist


## Begin session and set mode

Begins session for specified scenario. Client has to specify session name and
mode in request body. Session mode can be either 'record' and 'playback'.

* __URL__: /stubo/api/v2/scenarios/objects/<scenario_name>/action
* __Method__: POST
* __Response codes__:
  + __200__ - begins session
  + __400__ - something went wrong (e.g. session already exists)
* __Example request body__:
```javascript
{
  "begin": null,
  "session": "session_name",
  "mode": "record"
}
```
* __Example output__:
```javascript
{
  "version": "0.6.6",
  "error":
     {"message": "Scenario (localhost:scenario_10) has existing stubs, delete them before recording or create another scenario!",
     "code": 400}
}
```

## End session

Ends specified session. Client has to specify session name in request body.

* __URL__: /stubo/api/v2/scenarios/objects/<scenario_name>/action
* __Method__: POST
* __Response codes__:
  + __200__ - session ended.
* __Example request body__:
```javascript
{
  "end": null,
  "session": "playback_28"
}
```

* __Example output__:
```javascript
{
  "version": "0.6.6",
  "data": {
     "message": "Session ended"}
 }
```

## End all sessions for specific scenario

Ends all sessions for specified scenario

* __URL__: /stubo/api/v2/scenarios/objects/<scenario_name>/action
* __Method__: POST
* __Response codes__:
   + __200__ - scenario list with details returned
* __Example request body__:

```javascript
{
  "end": "sessions"
}
```

* __Example output__:

```javascript
{
  "version": "0.6.6",
  "data": {
      "playback_20": {"message": "Session ended"}
      }
}

```

## Add stub

Add stub to scenario

* __URL__: /stubo/api/v2/scenarios/objects/(?P<scenario_name>[^\/]+)/stubs
* __Method__: PUT
* __Response codes__:
   + __201__ - inserted
   + __200__ - updated or ignored
* __Example request body__:
```javascript
 {
     "request": {
         "method": "POST",
         "bodyPatterns": [
             { "contains": ["<status>IS_OK2</status>"] }
         ]
         },
     "response": {
         "status": 200,
         "body": "<response>YES</response>"
     }
 }
```
* __Example output__:
If updated (status code 200)
```javascript
{
    version: "0.7"
    data: {
    message: "updated with stateful response"
    }
 }
```

or inserted (status code 201).
```javascript
{
    version: "0.6.6"
    data: {
    message: "inserted scenario_stub: 55d5e7ebfc4562fb398dc697"
}
```

Here this ID - 55d5e7ebfc4562fb398dc697 is an object _id field from database. Proxy or an integrator could actually
go directly to database with this key and retrieve response.

## Getting response with stub

* __URL__: /stubo/api/v2/scenarios/objects/(?P<scenario_name>[^\/]+)/stubs
* __Method__: POST
* __Response codes__:
   + __*__ - any HTTTP response that user defined during stub insertion

* __Example request header__:
session: your_session_name

* __Example request body__:
```javascript
matcher here
```

## Getting request response data (JSON)

This call is similar to "Getting response with stub", however this one is intended to give all the data to the client
to build original response instead of returning original response. This enables storing encoded/encrypted responses.
Users have to provide a scenario:session key in headers.

* __URL__: /api/v2/matcher
* __Method__: POST
* __Response codes__:
   + __200__ - Response found
   + __404__ - Response not found

* __Example request header__:
session: scenario_name:session_name

* __Example request body__:
```javascript
matcher here
```

* __Example response body__:
```javascript
{
    "body": "body bytes or plain text here",
    "headers": {
                "key": "value",
                "key1": "value1"
                }
    "statusCode": 200
}

```


## Get all stubs for specific scenario

* __URL__: /stubo/api/v2/scenarios/objects/(?P<scenario_name>[^\/]+)/stubs
* __Method__: GET
* __Response codes__:
   + __200__ - stub list returned


```javascript
{
    "version": "0.7",
    "data": [
        {
            "stub": {
                "priority": -1,
                "request": {
                    "bodyPatterns": {
                        "contains": [
                            "<status>IS_OK2</status>"
                        ]
                    },
                    "method": "POST"
                },
                "args": {},
                "recorded": "2015-10-08",
                "response": {
                    "status": 123,
                    "body": "<response>YES</response>"
                }
            },
            "matchers_hash": "a92fa6cf96f218598d3723f2827a6815",
            "space_used": 219,
            "recorded": "2015-10-08",
            "scenario": "localhost:scenario_name_1"
        }
    ]
}
```

## Delete all scenario stubs

* __URL__: /stubo/api/v2/scenarios/objects/(?P<scenario_name>[^\/]+)/stubs
* __Method__: DELETE
* __Response codes__:
   + __200__ - stubs deleted
   + __409__ - precondition failed - there are active sessions either in playback or record mode

## Get delay policy list

Gets all defined delay policies

* __URL__: /stubo/api/v2/delay-policy/detail
* __Method__: GET
* __Response codes__:
   + __200__ - list with delay policies returned
* __Example output__:

```javascript
{
  "version": "0.6.6",
  "data": [
    {
      "delay_type": "fixed",
       "delayPolicyRef": "/stubo/api/v2/delay-policy/objects/slow",
      "name": "slow",
      "milliseconds": "1000"
    },
    {
      "delay_type": "fixed_2",
       "delayPolicyRef": "/stubo/api/v2/delay-policy/objects/slow",
      "name": "slower",
      "milliseconds": "5000"
    }
    ]
  }
```

## Get specific delay policy details

* __URL__: /stubo/api/v2/delay-policy/objects/<name>
* __Method__: GET
* __Response codes__:
   + __200__ - delay policy returned
   + __404__ - delay policy not found
* __Example output__:

```javascript
{
  "version": "0.6.6",
  "data": [
    {
      "delay_type": "fixed",
      "delayPolicyRef": "/stubo/api/v2/delay-policy/objects/slow",
      "name": "slow",
      "milliseconds": "1000"
    }
  ]
}
```

## Add delay policy

Creates a delay policy. Returns 201 status code if successful or 409 if request body options
are wrong (type fixed provided with mean and stddev options)

* __URL__: /stubo/api/v2/delay-policy
* __Method__: PUT
* __Response codes__:
   + __201__ - scenario list with details returned
   + __400__ - bad request
   + __409__ - wrong combination of options was used
* __Example request body__:
```javascript
{
  "name": "delay_name",
  "delay_type": "fixed",
  "milliseconds": 50
}
```

or:
```javascript
{
  "name": "delay_name",
  "delay_type": "normalvariate",
  "mean": "mean_value",
  "stddev": "val"
}
```

or:

```javascript
{
  "name": "weighted_delay_name",
  "delay_type": "weighted",
 "delays": "fixed,30000,5:normalvariate,5000,1000,15:normalvariate,1000,500,70"}
```


* __Example output__:

```javascript
{
  "status_code": 201,
  "version": "0.6.6",
  "data":
  {
    "status": "new",
    "message": "Put Delay Policy Finished",
    "delay_type": "fixed",
    "delayPolicyRef": "/stubo/api/v2/delay-policy/objects/my_delay",
    "name": "my_delay"
  }
}

```

## Delete delay policy

* __URL__: /stubo/api/v2/delay-policy/objects/<name>
* __Method__: DELETE
* __Response codes__:
   + __200__ - delay policy deleted
* __Example output__:

```javascript
{
  "version": "0.6.6",
  "data":
  {
    "message": "Deleted 1 delay policies from [u'my_delay']"
  }
}
```
