.. bookmarks

*********
Bookmarks
*********
Stub-O-Matic emulation of back-end services can be used for training courses.
Unlike automated tests, human students can make mistakes, try and step back to repeat 
steps or jump forward to a known state. Bookmarks enable this.

CAUTION: Bookmarking is an alpha feature and not fully tested in real life.

Background
==========
Software training on production systems has many challenges, one is the data to be used.
Training on live data has obvious issues: 

* students must not change real data
* students should not see confidential live data
* live data is dynamic, it is difficult to write repeatable training examples around changing data

Stubo can be used to feed the system being taught with repeatable data. A 
trainer can set up training scenarios using Stubo scenarios for the data. Each student
can start their own session which is a copy of the Stubo scenario data.

As the students click through the training examples they are likely to change the 
state in the Stubo responses. This happens behind the scenes just as it does for 
automated testing. 

Since each student has their own Stubo session, they each have their own data and 
can work at their own pace. Should a student want to go back to a particular state 
they can jump to a bookmark. Similarly, should the teacher want the whole class to 
jump to the end of a lesson, that can be done with Stubo bookmarks.

Creating
========

Bookmarks are created after stub creation. The teacher would begin a session in playback
mode and step through the lesson. At key points in the course, perhaps at the 
start of each lesson use the Stubo 'Bookmarks' tab to save a bookmark 
at this point in time for the session enabling students to jump to it later on. 

During the course delivery each student may have their own stubo session (data)
based on the bookmark created by the teacher. Students can jump to their own session
bookmarks setup by the teacher. If desired, students could create their own bookmarks
as well.

Export and Import
=================

When satisfied with stubs and bookmarks, end the playback session. 
When exporting a scenario any bookmarks associated with it will also be exported.

The .command file created on export includes the command to
load bookmarks. It is: ::

    import/bookmarks?location=bookmarks

Note when starting a session that includes bookmarks use: 'warm_cache=true' ::

     begin/session?scenario=trng&session=stud_1&mode=playback&warm_cache=true

Using
=====

During a playback session if a student wishes to jump to a bookmark they can 
go to the Stubo bookmarks page, select the desired bookmark then jump to it for 
their session. Should a teacher want to move the whole class to the same bookmark
that can be done in the same way.

Programatically the equivalent is: ::

    jump/bookmark?name=abc&session=joe&session=mary

