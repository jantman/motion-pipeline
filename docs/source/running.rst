.. _running:

Running
=======

Here's how to run it.

.. _running.motion_handler:

motion_handler.py
-----------------

``motion_handler.py`` is run automatically by ``motion`` when relevant events are fired. All that needs to be done is :ref:`install it <installation.motion_handler>`, :ref:`configure it and motion itself <configuration>`, and then run ``motion`` however is appropriate for your OS.

Celery Task Workers
-------------------

1. If you installed in a virtualenv, source it. Ensure you've run ``python setup.py develop`` or ``pip install motion-pipeline[worker]``
2. Ensure Redis is running and the ``REDIS_BROKER_URL`` setting is correct.
3. Ensure the path to your settings file is exported as ``MOTION_SETTINGS_PATH``
4. ``celery -A motion_pipeline.celerytasks.tasks worker --loglevel=info -Ofair -c 3``

Web Frontend
------------

1. If you installed in a virtualenv, source it. Ensure you've run ``python setup.py develop`` or ``pip install motion-pipeline[web]``
2. Ensure the path to your settings file is exported as ``MOTION_SETTINGS_PATH``
4. ``FLASK_APP=motion_pipeline.web.app flask run``
