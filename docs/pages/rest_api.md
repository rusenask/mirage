# Stub-O-Matic REST API v2

Stubo REST API v2 returns JSON. The response always returns the version, and payload. Responses are similar to
v1 API responses. The payload is either contained under 'data' if the response is successful or 'error' for
errors. Errors contain a descriptive message under 'message' and the http error code under 'code'.
Successful responses depend on the call made and are described below.

Encoding "application/json"

## Create scenario object

Creates scenario object. Client must specify scenario name in the request body.

* __URL__: /stubo/api/v2/scenarios
* __Method__: PUT
* __Body__:
    { “scenario”: “scenario_name” }
* __Response codes__:
   + __201__ - scenario created
   + __422__ - scenario with that name already exists
   + __400__ - something is missing (e.g. name)

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

# Get scenario details

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

# Delete scenario

Returns a list of scenarios with details.

* __URL__: /stubo/api/v2/scenarios/objects/<scenario_name>
* __Method__: DELETE
* __Response codes__:
   + __200__ - scenario deleted
   + __412__ - precondition failed - specified scenario does not exist


