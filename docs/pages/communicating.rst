.. communicating

*************************
Communicating with Mirage
*************************

Although Mirage has a GUI, it is best used for automated, repeatable interactions
with systems and test tools. Loading, calling and deleting of stubs should all 
be automated. Ideally your tests should be able to run overnight without human interaction.

Get/Response URLs
=================
Generally, MIrage uses URL arguments such as POST ::

    http://server/stubo/api/get/response?session=123. 

Additionally a get/response call can be POST ::

    http://server/stubo/api/get/response/YOUR/RANDOM/URL 

with the MIrage session in an HTTP Header xx_stb_session=123 (where xx can be any two characters).
In both cases the request text is in the HTTP body.

This allows request to be sent directly to MIrage from some systems without going through a MIrage integrator.

Virtual Mirage
==============

One MIrage server or cluster can support many tests, test environments and teams.
To help teams and users view only the stubs and sessions they are interested in,
a single physical MIrage server can be addressed by different URLs. 

For example http://stubo_1 and http://stubo_2 can point to the same physical machine.
Test team 1 could load a session 'test123' on http://stubo_1 and test team 2 could 
load an identically named session on http://stubo_2. These two session would be
treated completely independently by MIrage, as if they were on different hardware.

This allows for more efficient use of hardware and less software management overhead.
