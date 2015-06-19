
var auto_data = window._client_data || {}; 

var my_cluster = auto_data['data']['info']['cluster'] + ".*";
var graphite_url = auto_data['data']['info']['graphite_host'];


var servers = [my_cluster];   
    
var dashboards = build_dash(servers);    

function build_dash(servers) {
    var dashes = [];
    for (var i = 0; i < servers.length; i++) {
        server = servers[i];
        //alert("server: "+ server + " - " + graphite_url);
        parts = server.split(".");
        cluster = parts[0];
        host = parts[1];
        dashes[i] = { 
            "graphite_url": graphite_url,
            "name": server,  // give your dashboard a name (required!)
            "refresh": 5000,  // each dashboard has its own refresh interval (in ms)
            "metrics":  // metrics is an array of charts on the dashboards
            [
              {
                "alias": "stubs/second response rate",  // display name for this metric
                "targets": "sum(stats.timers.stubo." + server + ".stuboapi.get_response.latency.count_ps)",  // enter your graphite barebone target expression here
                "description": "response rate averaged over 10 seconds",  // enter your metric description here
                "renderer": "line",
                "height" : 200, 
                "colspan": 2,  
                //"summary": "avg",  // available options: [sum|min|max|avg|last|<function>]
                //"summary_formatter": d3.format(",f") // customize your summary format function. see d3 formatting docs for more options
              },
              {
                "alias": "delay added (ms)",
                "targets": "averageSeries(stats.timers.stubo."  + server + ".stuboapi.get_response.delay.mean)",   // see below for more advanced usage
                "description": "user requested delay added to responses",
                "height" : 200,
                "renderer": "line",  // use any rickshaw-supported renderer
                //"summary": "avg",
                "unstack": true,  // other parameters like unstack, interpolation, stroke, min, height are also available (see rickshaw documentation for more info)
              },
              {
                "alias": "latency (ms)",
                //"targets": "averageSeries(stats.timers.stubo."  + server + ".stuboapi.get_response.latency.upper_90)",   // see below for more advanced usage
                "targets": "averageSeries(stats.timers.stubo."  + server + ".stuboapi.get_response.latency.mean_90)",   // see below for more advanced usage
                "description": "latency average (excluding 10% outliers)",
                "height" : 200,
                "colspan": 2,  
                "renderer": "line",  // use any rickshaw-supported renderer
                //"summary": "avg",
                "unstack": true  // other parameters like unstack, interpolation, stroke, min, height are also available (see rickshaw documentation for more info)
              },

              {
                "alias": "request / response size (kb)",
                "targets": ["alias(averageSeries(stats.gauges.stubo."  + server + ".stuboapi.get_response.sent), 'sent')",
                            "alias(averageSeries(stats.gauges.stubo."  + server + ".stuboapi.get_response.received), 'received')"],   // see below for more advanced usage
                "description": "stub request and response sizes",
                "height" : 200,
                "renderer": "bar",  // use any rickshaw-supported renderer
                //"summary": "last",
                "unstack": true,  // other parameters like unstack, interpolation, stroke, min, height are also available (see rickshaw documentation for more info)
              },
              {
                "alias": "host response latency",
                "targets": "aliasByNode(stats.timers.stubo."  + server + ".stuboapi.get_response.latency.mean_90, 5)",   // see below for more advanced usage
                "description": "response latency by host ms",
                "height" : 250,
                "colspan": 2,  
                "renderer": "line",  // use any rickshaw-supported renderer
                //"summary": "last",
                "unstack": true  // other parameters like unstack, interpolation, stroke, min, height are also available (see rickshaw documentation for more info)
              },
              {
                "alias": "failure rate %",
                "targets": "divideSeries(sum(stats.stubo."  + cluster + ".*.stuboapi.*.success),sum(stats.stubo." + cluster + ".*.*.stuboapi.*.failure.*))",
                "description": "all functions failure rate %",
                "height" : 200,
                "renderer": "line",  // use any rickshaw-supported renderer
                //"summary": "last",
              },
              {
                "alias": "health checks (latency ms)",
                "targets": "stats.timers.stubo."  + cluster + ".*.stuboapi.get_status.latency.mean_90",
                "description": "get status health latency",
                "height" : 200,
                "renderer": "line",  // use any rickshaw-supported renderer
                //"summary": "last",
              },
              {
                "alias": "running put/stub count",
                "targets": "integral(sum(stats.stubo."  + server + ".stuboapi.put_stub.*))",  
                "description": "running put/stub count",
                "height" : 200,
                "renderer": "bar", 
                "summary": "last",
                "unstack": true  
              },
              {
                "alias": "running response count", 
                "targets": "integral(sum(stats.timers.stubo." + server + ".stuboapi.get_response.latency.count_ps))", 
                "description": "running get/response count", 
                "renderer": "bar",
                "height" : 200,  
                "summary": "last", 
                "summary_formatter": d3.format(",f") 
              },
            ]
        };
    }
    return dashes;
}


var scheme = [
              '#423d4f',
              '#4a6860',
              '#848f39',
              '#a2b73c',
              '#ddcb53',
              '#c5a32f',
              '#7d5836',
              '#963b20',
              '#7c2626',
              ].reverse();

function relative_period() { return (typeof period == 'undefined') ? 1 : parseInt(period / 7) + 1; }
function entire_period() { return (typeof period == 'undefined') ? 1 : period; }
function at_least_a_day() { return entire_period() >= 1440 ? entire_period() : 1440; }
