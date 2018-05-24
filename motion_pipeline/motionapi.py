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

import logging
import requests
import re

logger = logging.getLogger(__name__)


class MotionApiException(Exception):
    pass


class MotionApi(object):
    """
    Interface to motion's HTTP webcontrol API.
    """

    def __init__(self, host, port, cam_id, cam_name, timeout=2):
        self._host = host
        self._port = port
        self._cam_id = cam_id
        self._cam_name = cam_name
        self._timeout = timeout

    def _url(self, path):
        return 'http://%s:%s%s' % (self._host, self._port, path)

    def _do_get(self, path):
        r = requests.get(
            self._url(path), timeout=self._timeout
        )
        r.raise_for_status()
        return r

    def _get_detection_status(self):
        r = self._do_get('/0/detection/status')
        m = re.match(r'^Camera (\d+) Detection status (.+)$', r.text.strip())
        if not m:
            logger.error(
                'GET of %s returned non-matching detection status response: %s',
                r.url, r.text
            )
            raise MotionApiException(
                'Invalid detection status response: %s' % r.text
            )
        assert m.group(1) == '%d' % self._cam_id
        return m.group(2)

    def pause_detection(self):
        r = self._do_get('/0/detection/pause')
        expected = 'Camera %d -- %s Detection paused\nDone' % (
            self._cam_id, self._cam_name
        )
        if r.text.strip() != expected:
            logger.error(
                'GET %s to pause camera returned unexpected response: %s',
                r.url, r.text
            )
            raise MotionApiException(
                'Attempt to pause camera %s returned unexpected response: %s',
                self._cam_name, r.text
            )
        return True

    def resume_detection(self):
        r = self._do_get('/0/detection/start')
        expected = 'Camera %d -- %s Detection resumed\nDone' % (
            self._cam_id, self._cam_name
        )
        if r.text.strip() != expected:
            logger.error(
                'GET %s to resume camera %s returned unexpected response: %s',
                r.url, self._cam_name, r.text
            )
            raise MotionApiException(
                'Attempt to resume camera %s returned unexpected response: %s',
                self._cam_name, r.text
            )
        return True

    @property
    def detection_status(self):
        """
        Returns the detection status of the specified camera. Return value is
        a string, one of "PAUSE", "ACTIVE", or "UNKNOWN". The "UNKNOWN" string
        may optionally have further text appended to it.

        :return: detection status
        :rtype: str
        """
        s = self._get_detection_status()
        if s in ['PAUSE', 'ACTIVE']:
            return s
        return 'UNKNOWN: %s' % s
