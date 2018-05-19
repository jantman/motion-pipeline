.. _configuration:

Configuration
=============

.. _configuration.settings:

motion-pipeline settings file or module
---------------------------------------

``motion-pipeline`` is configured via a Python settings file. This file is imported by ``settings.py`` and can be specified as either a dot-delimited importable python module or the absolute path to a Python source file on disk (if using a source file, it must be specified as an absolute path). The configuration file can be set either via the ``MOTION_SETTINGS_PATH`` environment variable or via the ``-c`` / ``--config`` options to most of the entrypoint scripts.

Note that this file is imported whenever ``motion`` sends an event to ``motion-handler``. While it *can* include any Python code, it should be as simple and fast-loading as possible.

An example file is in the motion-pipeline source as ``settings_example.py``; you should copy that file as an example and edit as necessary.

.. _configuration.motion:

Configuration of Motion Itself
------------------------------

Configuration of ``motion`` itself involves setting the correct event handler commands to point to ``motion_handler.py`` and pass the required arguments. See the example below.

.. _configuration.example_motion_conf:

Example motion.conf
+++++++++++++++++++

The only parts of ``motion.conf`` that are specific to motion-pipeline are the various ``on_*`` options that tell motion to execute our handler when various events occur:

.. literalinclude:: example_motion.conf
   :linenos:
   :lines: 555-612
