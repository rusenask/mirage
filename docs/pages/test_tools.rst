.. test_tools

***************************
Integration with Test Tools
***************************

Stub-O-Matic works with all major software test execution tools. Stubo, of course,
does not run tests or evaluate results, it emulates back-end systems needed by
tests.

Data dependent software tests typically consist of 3 steps.

1. Data setup
2. Test execution
3. Data teardown

Working with Stubo to provide back-end data is no different.

Stubo's API can be used to setup or teardown data directly. Stubo command files
offer a shorthand for using the API and are much more compact. Any test tool that
can make HTTP calls can use Stubo.

Test steps example
==================

1. Trigger an http call similar to this from the test tool of your choice: :: 
   
  http://mystubo.com/stubo/api/exec/cmds?cmdfile=http://my_stubs/checkin_setup.commands

2. Run tests
3. Trigger a teardown http call similar to this from the test tool: :: 
   
  http://mystubo.com/stubo/api/exec/cmds?cmdfile=http://my_stubs/checkin_teardown.commands

Refer to the worked case study for setup and teardown examples.
