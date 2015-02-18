.. examples

Examples
************
Lots of example usage of Stubo can be found under /static/cmds/tests. The folders
under here contain various cmd scripts and their associated files (requests, matchers, responses)
and user exit code examples. 

You can run these scripts from the Manage page


.. _daterolling:

Templates Date Rolling
======================

Shows how you can roll a date using the difference of recorded and play dates.

.. code-block:: javascript
 
    Run /static/cmds/tests/templates/dateroll/first.commands

Stateful stubs
==============

Shows how the same request can return different responses.

.. code-block:: javascript

    Run /static/cmds/tests/state/converse.commands

user exit using XSLT
======================

Example showing how the same request but with different
environmental data can be transformed by 'templating' the env values in
the matcher & response during put/stub and transforming it with XSLT using 
the env values from request_text during get/response. 

.. code-block:: javascript

    Run /static/cmds/tests/ext/xlst/first.commands

User exit using a cache
=======================

.. code-block:: javascript

    Run /static/cmds/tests/ext/cache/1.commands