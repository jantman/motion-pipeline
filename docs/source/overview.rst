.. _overview:

Overview
========

I have two IP cameras at home that I'd like to use for security, specifically motion-activated recording and notification of events when I'm away. The cameras (see my detailed unboxing/review of them `on my blog <https://blog.jasonantman.com/2018/05/amcrest-ip-camera-first-impressions/>`_) are 960P and 1080P, respectively. The `current options <https://blog.jasonantman.com/2018/05/linux-surveillance-camera-software-evaluation/>`_ for Free/Open Source software to do this aren't adequate for me; ZoneMinder, the de-facto standard, doesn't meet my resource constraints of being able to run on (or partially run on) a RaspberryPi 3 B+ and the other options I could find aren't mature or lack features I need.

As a result, I'm building this. It's a project composed of multiple services and intended to handle processing data from Motion (recordings and the metadata associated with them), storing it, and providing a viewing interface and notifications/alerts. The project is intended to be modular, utilizing a storage service (S3 or the local S3-compatible `minio <https://www.minio.io/>`_), a queue (Redis) and a database (MySQL) to connect a handler that runs on the same device as ``motion`` (this could be anything from a RaspberryPi to a server), an asynchronous task worker for ingesting new data from motion, triggering notifications, and generating thumbnails, and a web frontend.

The architecture is intended to be decoupled, equally happy on a single fanless computer or in the cloud, and to allow separating realtime tasks (``motion`` for motion detection and recording, and ingesting its recordings and metadata into the system) from less-time-sensitive tasks (generating thumbnails for videos, etc.) and the user interface.

Architecture
------------

Motion Ingest
+++++++++++++

.. literalinclude:: ingest.txt

User Interface and Notifications
++++++++++++++++++++++++++++++++

TBD.
