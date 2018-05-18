motion-pipeline
===============

.. image:: https://img.shields.io/pypi/v/python-package-skeleton.svg?maxAge=2592000
   :target: https://pypi.python.org/pypi/python-package-skeleton
   :alt: pypi version

.. image:: http://www.repostatus.org/badges/latest/wip.svg
   :alt: Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.
   :target: http://www.repostatus.org/#wip

Frontend and recording management pipeline for the Motion video motion detection project.

**Docs:** `https://motion-pipeline.readthedocs.io/en/latest/ <https://motion-pipeline.readthedocs.io/en/latest/>`_

Status
------

This project is **alpha** code, and is a **work in progress that may not be finished.** I am going to be doing as much as I can on this in three weeks; I'm not sure if I'll continue work on it after that. You've been warned. Sorry.

Introduction
------------

I have two IP cameras at home that I'd like to use for security, specifically motion-activated recording and notification of events when I'm away. The cameras (see my detailed unboxing/review of them `on my blog <https://blog.jasonantman.com/2018/05/amcrest-ip-camera-first-impressions/>`_) are 960P and 1080P, respectively. The `current options <https://blog.jasonantman.com/2018/05/linux-surveillance-camera-software-evaluation/>`_ for Free/Open Source software to do this aren't adequate for me; ZoneMinder, the de-facto standard, doesn't meet my resource constraints of being able to run on (or partially run on) a RaspberryPi 3 B+ and the other options I could find aren't mature or lack features I need.

As a result, I'm building this. It's a project composed of multiple services and intended to handle processing data from Motion (recordings and the metadata associated with them), storing it, and providing a viewing interface and notifications/alerts. The project is intended to be modular, utilizing a storage service (S3 or the local S3-compatible `minio <https://www.minio.io/>`_), a queue (Redis) and a database (MySQL) to connect a handler that runs on the same device as ``motion`` (this could be anything from a RaspberryPi to a server), an asynchronous task worker for ingesting new data from motion, triggering notifications, and generating thumbnails, and a web frontend.

Documentation
-------------

Full documentation for this project is hosted on ReadTheDocs at `https://motion-pipeline.readthedocs.io/en/latest/ <https://motion-pipeline.readthedocs.io/en/latest/>`_.

Bugs and Feature Requests
-------------------------

Bug reports and feature requests are happily accepted via the `GitHub Issue Tracker <https://github.com/jantman/python-package-skeleton/issues>`_. Pull requests are
welcome. Issues that don't have an accompanying pull request will be worked on
as my time and priority allows.
