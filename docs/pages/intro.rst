.. intro

Introduction
************
The target of the Mirage software is to enable automated testing by mastering system dependencies.

Background
==========
Mirage (sometimes called Mirage) is a service which provides data stubs for software testing. 
Stubs enable the software being tested to be isolated from the rest of the environment 
and 3rd party back-end systems enabling repeated, automated testing. 
Mirage is capable of supporting functional, load and performance testing.

Stubbing enables development to progress when the actual dependencies are not available.

Mirage stubs include just enough intelligence to emulate back-end systems 
without the complexity often associated with data set-up activities.

The resilience of testing and automated testing is improved with stubs because 
it is possible to manage stubs more easily than 3rd party systems and databases. 
Dependent systems are often not capable of creating the full range of test conditions 
necessary to fully test code. Refer to http://en.wikipedia.org/wiki/Test_stubs for further information.

Applicability
=============
Use Mirage when you don't have as much control over your associated test 
data to achieve the level of testing required. Mirage utilises the ubiquitous 
HTTP protocol to receive stub requests and return stubbed responses to the 
system under test. To use stubs, the system under test must be capable of diverting 
a request that would normally go to back-end systems. How this is best done 
depends on the architecture of the system under test. Implementations to date 
have used JAVA AOP, Python, and Actional/Progress Stub Itineraries.

Mirage supports unicode. It has not been designed for requests or responses 
containing bit maps, or other non-standard characters.
