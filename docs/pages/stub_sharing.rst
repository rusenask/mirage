.. stub_sharing

*************
Sharing Stubs
*************

Mirage allows stubs to be organised and shared in ways to suit a project's
test data needs. Mirage is about emulating back-end system behaviour and as such,
stubs can be organised around individual services provided by a given back-end 
service. These stubs can be assembled and re-used as required by individual tests.

Another option is for each test to own its own stubs. This  makes each test and
its data independent from all others, but can also lead to an explosion of stubs and
potential management issues if they need to be upgraded to changes in the 
back-end system.

As an example, consider an end to end use case for a Game Leader application as follows:
Test 4 - Change leader

GIVEN current (10 July) leader is Bob

WHEN current leader is requested

THEN leader is Bob

WHEN Sue enters a score of 1000 for 10 July

WHEN current leader is requested

THEN leader is now Sue

This test uses both the increment_score service and the view_leader service.
Many stubs from the other tests can be reused and will be by creating a new command
file.

Mirage command files can use stubs from folders relative to the command file location
or by URL. Refer to the 'Commands' section of this documentation for details.

change_setup.commands: ::

  # load and test stubs for change leader test
  delete/stubs?scenario=change_leader
  begin/session?scenario=change_leader&session=change_leader&mode=record

  # add points to bob on the 10th July
  put/stub?session=change_leader,increment/incr_bob_10th_6.textMatcher,increment/incr_bob_10th_6.response

  # find leader on 10th ( it is bob)
  put/stub?session=change_leader,leader/lead_1.textMatcher,leader/lead_1.response

  # add 1000 points to Sue
  put/stub?session=change_leader,incr_sue_10th_1000.textMatcher,incr_sue_10th_1000.response

  # find leader on 10th ( it is now Sue)
  put/stub?session=change_leader,leader/lead_1.textMatcher,leader_is_sue.response

  end/session?session=change_leader

  begin/session?scenario=change_leader&session=change_leader&mode=playback

change_responses.commands: ::

  # increment Bob's score by 6 points, first entry for day so should return 6
  get/response?session=change_leader,increment/incr_bob_10th_6.request

  # find the leader
  get/response?session=change_leader,leader/lead_1.request

  # increment Sue's score by  1000 points
  get/response?session=change_leader,incr_sue_10th_1000.request

  # find the leader
  get/response?session=change_leader,leader/lead_1.request

change_teardown.command: ::

  end/session?session=change_leader
  delete/stubs?scenario=change_leader

incr_sue_10th_1000.request: ::

  <incrementScore>
    <date>2013-07-10</date>
    <contestant>sue</contestant>
    <incrementby>1000</incrementby>
    <authentication_code>23455672213456</authentication_code>
    <gameId>1234</gameId>
  </incrementScore>

incr_sue_10th_1000.textMatcher: ::

  <incrementScore>
    <date>2013-07-10</date>
    <contestant>sue</contestant>
    <incrementby>1000</incrementby>

incr_sue_10th_1000.response: ::

  <incrementScore>
    <date>2013-07-10</date>
    <contestant>sue</contestant>
    <new_score>1000</new_score>
    <authentication_code>23455672213456</authentication_code>
    <gameId>1234</gameId>
  </incrementScore>

leader_is_sue.response: ::

  <leader>
  <boardId>1234</boardId>
    <contestant>sue</contestant
    {% if stubbedToday.day == 1 %}
    <prevMonthWinner>sally</prevMonthWinner>
    {% end %}
  </leader>

These stubs and command files show how Mirage can mingle stubs provided at a service 
function level with stubs specific to a given test.
