Stub-O-Matic
============

[![Build Status](https://travis-ci.org/Stub-O-Matic/stubo-app.png?branch=master)](https://travis-ci.org/Stub-O-Matic/stubo-app)
[![Documentation Status](https://readthedocs.org/projects/stubo-app/badge/?version=latest)](https://readthedocs.org/projects/stubo-app/?badge=latest)

Enable automated testing by mastering system dependencies.
Use when reality is simply not good enough.

## Documentation


See the The documentation [readthedocs](<http://stubo-app.readthedocs.org/en/latest/>) to view
user documentation.


## Install and run (Docker + Docker Compose)

Install Docker and Docker Compose.

* cd to project root
* docker-compose up
* [http://localhost:8001] or if you are using boot2docker (Mac OSX) - check VM's IP address with command:
  $ boot2docker ip

## Install (Manual)

(Linux Red Hat Enterprise, CentOS, Fedora, or Amazon Linux). It's easier when using python virtualenv wrapper, get more 
information about installing and using it here: [https://virtualenvwrapper.readthedocs.org/en/latest/]

Redis Server Installation::

    $ sudo yum install redis-server
    $ sudo service redis-server start

Mongo server Installation::

    $ sudo yum install mongodb-org
    $ sudo service mongod start | stop

dependencies::

    $ sudo yum install python27-virtualenv libxslt libxslt-devel libxml2 libxml2-devel texlive-full


(Linux Ubuntu) 

Redis Server Installation::

    $ sudo apt-get install -y redis-server
    $ sudo service redis-server start

Mongo server Installation::

    $ sudo apt-get install -y mongodb-org
    $ sudo service mongod start | stop
    
dependencies::

    $ sudo apt-get install -y python-dev python-pip wget python2.7-dev libxml2 libxml2-dev libxslt1-dev
    
Download application:

       
    (env) $ git clone https://github.com/Stub-O-Matic/stubo-app.git
    
    (env) $ cd stubo-app
    
    (env) $ mkv
    
    (env) $ pip install -r requirements/development.txt  (in production environment use pip install -r requirements.txt)
    

> Installing lxml library on OSX:
> export CFLAGS=-Qunused-arguments
> export CPPFLAGS=-Qunused-arguments
>
> pip install lxml
> or following if installing globally
> sudo pip install lxml

### RUN

Perform the following::

    $ sudo service mongod start
    $ sudo service redis-server start

Active your virtual python env:

    $ workon env
    
Launch run.py in project root:
   
    $ python run.py
    
Logs are in _PROJECT_ROOT_/log/stubo.log
Default config is picked up from _PROJECT_ROOT_/dev.ini     
Alternatively you can run from another location:

    (env) $ python run.py -c path_to_config


## FUNCTIONAL TESTING

You can run the test suite by running the following command 
(in the project root: stubo-app)::

        (env) $ nosetests stubo

Use the ``-x`` flag to stop the tests at the first error::

        (env) $ nosetests stubo -x
        
Or to run a specific test:

         (env) $ nosetests stubo.tests.integration.test_api:TestAcceptance.test_exec_first_commands

Use the ``--with-coverage`` flag to display a coverage report after
running the tests, this will show you which files / lines have not
been executed when the tests ran::

        (env) $ nosetests stubo --with-coverage --cover-package=stubo

Or to run a specific test:

        (env) $ nosetests stubo.tests.integration.test_api:TestAcceptance.test_exec_first_commands
        
and code analysis 

        (env) $ pylint stubo
        
## DEBUGGING

If you want to call functions to debug in a python shell and they have a 
dependency on redis or mongo you must initialise them first

    from stubo.utils import start_redis
    slave, master = start_redis({})
    slave
    <redis.client.Redis object at 0x10168e650> 
    
    from stubo.utils import init_mongo
    dbclient = init_mongo()
    dbclient
    Database(MongoClient('localhost', 27017), u'stubodb')

Now you can make calls that use redis

    >>> from stubo.cache import Cache
    >>> cache = Cache(host='localhost')
    >>> cache.get_session('first', 'first_1')
        {u'status': u'dormant', u'system_date': u'2015-02-24', u'scenario': u'localhost:first', u'last_used': u'2015-02-24 11:19:21', u'scenario_id': u'54ec5e3981875908f911a71b', u'session': u'first_1'}

& mongodb

    from stubo.model.db import Scenario
    scenario = Scenario()
    stubs = list(scenario.get_stubs('localhost:first'))
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(stubs[0])
    {   u'_id': ObjectId('537c8f1cac5f7303ad704d85'),
        u'scenario': u'localhost:first',
        u'stub': {   u'recorded': u'2014-05-21',
                     u'request': {   u'bodyPatterns': [   {   u'contains': [   u'get my stub\n']}],
                                     u'method': u'POST'},
                     u'response': {   u'body': u'Hello {{1+1}} World\n',
                                      u'delayPolicy': u'slow',
                                      u'status': 200}}}
    
    from stubo.model.db import Tracker
    tracker = Tracker()
    list(tracker.find_tracker_data({'function' : 'get/response'}, 0, 1))
    [{u'function': u'get/response', u'scenario': u'conv', u'start_time': datetime.datetime(2013, 10, 29, 10, 38, 16, 534000, tzinfo=<bson.tz_util.FixedOffset object at 0x1015b6910>), u'return_code': 200, u'session': u'mary', u'duration_ms': 5, u'stubo_response': u'a2 response\n', u'_id': ObjectId('526f90180cfb4403fc27c0fa')}]
       
        
## PERFORMANCE TESTING

Load performance test data (over 10,000 stubs in 100 scenarios) with 

        stubo/api/exec/cmds?cmdfile=/static/cmds/perf/perf_setup.commands 
        this will take some time to run and leaves 100 sessions in playback mode.

        optionally demonstrate that the load was successfull with:
        stubo/api/exec/cmds?cmdfile=/static/cmds/perf/perf_getresponse.commands
        this gets one response from each session.

        When finished end sessions and delete stubs with:
        stubo/api/exec/cmds?cmdfile=/static/cmds/perf/perf_teardown.commands

## ANALYTICS
 
Certain Metrics are extracted from the track record and sent via UDP to a 
statsd server which aggregates the stats every 10 seconds before sending to 
a graphite carbon server via TCP. 

The location of the statsd server and metrics prefix to use
is specified in the stubo ini file

    statsd.host = localhost
    statsd.prefix = stubo
    
An analytics dashboard is provided to see that stats. Graphite connection 
details are specified in the stubo ini file::

    graphite.host = http://your-stubo-graphite.com/
    # auth to connect to graphite server if required 
    graphite.user = <user>
    graphite.password = <passwd>     

## DOCUMENTATION

Documentation is generated with Sphinx. The doc sources are located under /docs.

prereq for generating PDF:

    $ yum install texlive

To generate docs

    (env) $ python setup.py build_sphinx --build-dir=./stubo/static/docs

To generate PDF

       $ cd docs
       $ make latexpdf
       $ cp _build/latex/Stub-O-Matic.pdf ../stubo/static/docs

## PROFILING

Stubo profiling is available via two different profilers yappi and plop. 

yappi function stats

    name: name of the function being profiled
    #n: is the total callcount of the function.
    tsub: total spent time in the function minus the total time spent in the other functions called from this function.
    ttot: total time spent in the function.
    tavg: is same as ttot/ccnt. Average total time.

Plop is a stack-sampling profiler for Python. Profile collection can be turned on and off in a live process with minimal performance impact.

Both profilers are enabled via an HTTP inteface in stubo.

yappi - generate stats for 3 mins, output is saved to a csv file: 

    _profile?interval=180

plop - generate stats for 3 mins, output is saved by default to /tmp/plop.out:
    
    _profile2?interval=180&output=/tmp/plop.out

To view plop results in a bubble graph:

    (env) $ python -m plop.viewer --datadir=/tmp

View via the plop app at http://localhost:8888

### Authors

Stub-O-Matic is made available by [OpenCredo](http://opencredo.com)
and a team of contributors.

### License

Stub-O-Matic is offered under GPLv3, see LICENSE for more details.