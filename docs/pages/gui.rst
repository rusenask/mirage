.. gui

***
GUI
***

Tracker
=======

The Mirage 'Tracker' page shows details of all requests submitted to Mirage 
and the received response. Click on the link in the function column to show a 
detailed view. Debug level tracking can be added to a get/response call if 
'tracking_level=full' is added to the call. Matching errors will also trigger 
some extra debug data to be added to a normal track record.

Mirage can not keep tracker data forever so it will eventually drop off the server
as space is used up. 

The tracker page shows all Mirage actions performed on the server. Filters are
provided to filter on session, datetime, response times and errors. 

To go into detail on a particular transaction click the link in the 'Function' column
or 'Details' in the 'Mirage Response' column. For a get/response call the
matchers and responses for the call can be found from the >>> view scenario 
details (stub matchers and responses) link at the top of the details page.

Filtering: The tracker filter fields should be self explanatory. By default, the 
tracker page shows only data sent to the Mirage URL, shown at the top of the browser.
To see tracker items from other URLs on the same hardware, tick the 'All Hosts' box.

Manage 
======

The manage page allows users to execute command files and view system state.

The list of loaded stubs includes the date the stubs were loaded into Mirage and the last
time the stub was used. Clicking the scenario name shows the stored matchers and
responses for the scenario.

Also available is a command file scratchpad for entering one or more commands. 
For example, one could enter: ::

    end/session?session=first_session
    delete/stubs?scenario=first
    end/session?session=second_session
    delete/stubs?scenario=second

All the above commands would then be executed. See the results on the tracker page.

The manage page also shows stubs, delay policies and any external modules loaded.

Analytics
=========
The 'Analytics' tab takes you to a dashboard showing statistics about the Mirage server. The orange bar along the top allows you to select different Mirage
servers and time periods. The first of the 4 squares on the right turns on a legend.

Charts:

========================== ===========
chart title                description
========================== ===========
stubs/second response rate number of stubs requested per second
delay added                user defined delays to stubs, these can be specified   to emulate response times of the system being stubbed
latency                    average time taken to return a stub, excluding network and user defined delays
request/response size      size in kb of the requests to mirage and responses delivered
host response latency      where Mirage is deployed across    multiple servers this chart compares the different servers against each other
failure rate %             percent of failed requests (HTTP response >= 400)
health checks              Mirage has a regular health check ping to demonstrate that all systems are working properly
running put/stub count     cumulative total of stubs loaded
running response count     cumulative total of stubs retrieved
========================== ===========

Also note the Mirage API documentation for get/stats.
