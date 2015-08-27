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
    # bookmarks
    ("/stubo/api/put/bookmark", "PutBookmarkHandler"),
    ("/stubo/api/get/bookmarks", "GetBookmarksHandler"),
    ("/stubo/api/jump/bookmark", "JumpBookmarkHandler"),
    ("/stubo/api/delete/bookmark", "DeleteBookmarkHandler"),
    ("/stubo/api/import/bookmarks", "ImportBookmarksHandler"),
    # exec commands
    ("/stubo/default/execCmds", "StuboCommandHandler"),
    ("/stubo/api/exec/cmds", "StuboCommandHandler"),
]

# used for API v2
rest_api = [
    # scenario controls
    ("/stubo/api/v2/scenarios", "BaseScenarioHandler"),
    ("/stubo/api/v2/scenarios/detail", "GetAllScenariosHandler"),
    ("/stubo/api/v2/scenarios/objects/(?P<scenario_name>[^\/]+)/action", "ScenarioActionHandler"),
    ("/stubo/api/v2/scenarios/objects/(?P<scenario_name>[^\/]+)", "GetScenarioDetailsHandler"),
    # stub controls
    ("/stubo/api/v2/scenarios/objects/(?P<scenario_name>[^\/]+)/stubs", "StubHandler"),
    # delay policy controls
    ("/stubo/api/v2/delay-policy", "CreateDelayPolicyHandler"),
    ("/stubo/api/v2/delay-policy/detail", "GetAllDelayPoliciesHandler"),
    ("/stubo/api/v2/delay-policy/objects/(?P<delay_policy_name>[^\/]+)", "GetDelayPolicyDetailsHandler"),

]

# UI pages
ui_pages = [
    ("/tracker", "ViewTrackerHandler"),
    ("/tracker/(.*)", "ViewATrackerHandler"),
    ("/", "HomeHandler"),
    ("/manage", "ManageHandler"),
    ("/manage/exec_cmds", "StuboCommandHandlerHTML"),
    ("/bookmarks", "BookmarkHandler"),
    ("/docs", "DocsHandler"),
    ("/stubs", "GetStubListHandlerHTML"),
    ("/analytics", "AnalyticsHandler"),
    ('/_profile', 'ProfileHandler'),
    ('/_profile2', 'PlopProfileHandler'),
]

url_patterns = json_api + rest_api + ui_pages