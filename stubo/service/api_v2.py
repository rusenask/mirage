"""  
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""

from stubo.model.db import (
    Scenario, get_mongo_client, session_last_used, Tracker
)

from stubo.model.stub import Stub, StubCache, parse_stub
from stubo import version


def scenario_data(host):
    response = {'version' : version}
    scenario_db = Scenario()
    if host == 'all':
        scenarios = [x['name'] for x in scenario_db.get_all()]
    else:
        # get all scenarios for host
        scenarios = [x['name'] for x in scenario_db.get_all(
            {'$regex': '{0}:.*'.format(host)})]
    response['data'] = dict(host=host, scenarios=scenarios)
    return response