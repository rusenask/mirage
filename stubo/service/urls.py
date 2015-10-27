# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2015 by OpenCredo.
    :license: GPLv3, see LICENSE for more details.
"""

# Legacy API
json_api = [
    ("/stubo/api/get/status", "GetStatusHandler"),
    # sessions
    ("/stubo/api/begin/session", "BeginSessionHandler"),
    ("/stubo/api/end/session", "EndSessionHandler"),
    ("/stubo/api/end/sessions", "EndSessionsHandler"),
    # stubs
    ("/stubo/api/get/response", "GetResponseHandler"),
    ("/stubo/api/get/response/.*", "GetResponseHandler"),
    ("/stubo/api/put/stub", "PutStubHandler"),
    # scenarios
    ("/stubo/api/delete/stubs", "DeleteStubsHandler"),
    ("/stubo/api/get/stubcount", "GetStubCountHandler"),
    ("/stubo/api/get/stublist", "GetStubListHandler"),
    ("/stubo/api/get/scenarios", "GetScenariosHandler"),
    ("/stubo/api/put/scenarios/(?P<scenario_name>[^\/]+)", "PutScenarioHandler"),
    # misc
    ("/stubo/api/get/export", "GetStubExportHandler"),
    ("/stubo/api/get/stats", "GetStatsHandler"),
    # delay policies
    ("/stubo/api/put/delay_policy", "PutDelayPolicyHandler"),
    ("/stubo/api/get/delay_policy", "GetDelayPolicyHandler"),
    ("/stubo/api/delete/delay_policy", "DeleteDelayPolicyHandler"),
    # api version
    ("/stubo/api/get/version", "GetVersionHandler"),
    # modules
    ("/stubo/api/put/module", "PutModuleHandler"),
    ("/stubo/api/delete/module", "DeleteModuleHandler"),
    ("/stubo/api/delete/modules", "DeleteModulesHandler"),
    ("/stubo/api/get/modulelist", "GetModuleListHandler"),
    # settings
    ("/stubo/api/put/setting", "PutSettingHandler"),
    ("/stubo/api/get/setting", "GetSettingHandler"),
    # exec commands
    ("/stubo/default/execCmds", "StuboCommandHandler"),
    ("/stubo/api/exec/cmds", "StuboCommandHandler"),
]

# used for API v2
rest_api = [
    # scenario controls
    ("/api/v2/scenarios", "BaseScenarioHandler"),
    ("/api/v2/scenarios/detail", "GetAllScenariosHandler"),
    ("/api/v2/scenarios/upload", "ScenarioUploadHandler"),
    ("/api/v2/scenarios/objects/(?P<scenario_name>[^\/]+)/action", "ScenarioActionHandler"),
    ("/api/v2/scenarios/objects/(?P<scenario_name>[^\/]+)", "GetScenarioDetailsHandler"),
    # stub controls
    ("/api/v2/scenarios/objects/(?P<scenario_name>[^\/]+)/stubs", "StubHandler"),
    # delay policy controls
    ("/api/v2/delay-policy", "CreateDelayPolicyHandler"),
    ("/api/v2/delay-policy/detail", "GetAllDelayPoliciesHandler"),
    ("/api/v2/delay-policy/objects/(?P<delay_policy_name>[^\/]+)", "GetDelayPolicyDetailsHandler"),
    # external modules
    ("/api/v2/modules", "ExternalModulesHandler"),
    ("/api/v2/modules/objects/(?P<module_name>[^\/]+)", "ExternalModuleDeleteHandler"),
    # asynchronous matcher
    ("/api/v2/matcher", "ScenarioStubMatcher"),
    # tracker records
    ("/api/v2/tracker/records", "TrackerRecordsHandler"),
    ("/api/v2/tracker/records/objects/(?P<record_id>[^\/]+)", "TrackerRecordDetailsHandler"),
    # websocket tracker api
    ("/api/ws/tracker", "TrackerWebSocket")
]

# UI pages
ui_pages = [
    ("/analytics", "AnalyticsHandler"),
    ('/_profile', 'ProfileHandler'),
    ('/_profile2', 'PlopProfileHandler'),
    # management
    # currently routing to tracker page
    ("/", "TrackerHandler"),

    ("/manage/scenarios", "ManageScenariosHandler"),
    ("/manage/scenarios/details", "ManageScenarioDetailsHandler"),
    ("/manage/scenarios/export", "ManageScenarioExportHandler"),

    ("/manage/delaypolicies", "ManageDelayPoliciesHandler"),
    ("/manage/modules", "ManageModulesHandler"),
    # commands handlers
    ("/manage/commands", "ManageCommandsHandler"),
    ("/manage/execute", "ExecuteCommandsHandler"),

    # tracker
    ("/tracker", "TrackerHandler"),
    ("/tracker/objects", "TrackerDetailsHandler"),

]

url_patterns = json_api + rest_api + ui_pages
