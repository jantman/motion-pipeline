"""
The latest version of this package is available at:
<http://github.com/jantman/motion-pipeline>

##################################################################################
Copyright 2018 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of motion-pipeline, also known as motion-pipeline.

    motion-pipeline is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    motion-pipeline is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with motion-pipeline.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
##################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/motion-pipeline> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
##################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
##################################################################################
"""

import os
import logging
from datetime import datetime
from tempfile import mkstemp
from contextlib import contextmanager

logger = logging.getLogger(__name__)


def fix_werkzeug_logger():
    """
    Remove the werkzeug logger StreamHandler (call from ``app.py``).

    With Werkzeug at least as of 0.12.1, werkzeug._internal._log sets up its own
    StreamHandler if logging isn't already configured. Because we're using
    the ``flask`` command line wrapper, that will ALWAYS be imported (and
    executed) before we can set up our own logger. As a result, to fix the
    duplicate log messages, we have to go back and remove that StreamHandler.
    """
    wlog = logging.getLogger('werkzeug')
    logger.info('Removing handlers from "werkzeug" logger')
    for h in wlog.handlers:
        wlog.removeHandler(h)


def dtnow():
    """
    Return the current datetime as a timezone-aware DateTime object in UTC.

    :return: current datetime
    :rtype: datetime.datetime
    """
    return datetime.now()


@contextmanager
def autoremoving_tempfile(suffix=None):
    fd, path = mkstemp(prefix='motion-pipeline', suffix=suffix)
    os.close(fd)
    try:
        yield path
    finally:
        os.unlink(path)


@contextmanager
def in_directory(path):
    pwd = os.getcwd()
    os.chdir(path)
    yield os.path.abspath(path)
    os.chdir(pwd)
