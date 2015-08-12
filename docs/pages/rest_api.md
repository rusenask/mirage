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

