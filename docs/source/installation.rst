.. _installation:

Installation
============

motion-pipeline is made up of three overall components that can be installed separately: ``motion_handler.py`` (the script used by ``motion`` itself in the ``on_*`` settings), the task worker, and the web frontend.

Requirements
------------

* Python 3.4+ (currently tested with 3.4, 3.5, 3.6) and ``pip``
* Python `VirtualEnv <http://www.virtualenv.org/>`_ (recommended installation method; your OS/distribution should have packages for these)
* `motion <https://motion-project.github.io/>`_ on the system that will run the motion-handler
* Redis and MySQL on *some* system (can be colocated with any of these components, or completely separate system(s))

For installations other than on RaspberryPi or similar dedicated systems, it's recommended that you install into a virtual environment (virtualenv / venv). See the `virtualenv usage documentation <http://www.virtualenv.org/en/latest/>`_ for information on how to create a venv.

To install the requirements for ``motion-handler`` on a RaspberryPi running Raspbian Stretch (``2018-04-18-raspbian-stretch-lite`` image) I did the following:

1. ``wget https://github.com/Motion-Project/motion/releases/download/release-4.1.1/pi_stretch_motion_4.1.1-1_armhf.deb && sudo apt install ./pi_stretch_motion_4.1.1-1_armhf.deb`` - this installs the ``motion`` [4.1.1 package from GitHub](https://github.com/Motion-Project/motion/releases/tag/release-4.1.1), which includes some important fixes over the 4.0-1 package in the Raspbian Stretch repositories.
2. ``sudo apt-get install python3-pip git python3-dev``

If you don't have them installed already, you may need to install the common build tools on your OS.

Installation of Dependencies
----------------------------

* To install motion-pipeline and only the dependencies for ``motion_handler.py``: ``pip install motion-pipeline``
* To install motion-pipeline and the dependencies for the task worker: ``pip install motion-pipeline[worker]``
* To install motion-pipeline and the dependencies for the web frontend: ``pip install motion-pipeline[web]``
* To install all of the above: ``pip install motion-pipeline[all]``

Installation of motion_handler.py
---------------------------------

I haven't had time to write real installation tooling for this yet. In the mean time, on the computer where you'll be running ``motion``:

1. ``pip install motion-pipeline``
2. Find and record the absolute path to the ``motion-handler`` entrypoint: ``which motion-handler``
3. Copy your :ref:`configuration.settings` somewhere on that machine (as an example, we put it at ``/etc/motion-pipeline_settings.py``).
4. Set up your ``motion.conf`` file for motion. Specify the various ``on_*`` configuration settings to point to the path to the motion-handler entrypoint and set the ``--config`` option to the path to your settings file/module. See :ref:`configuration.example_motion_conf` for an example.
