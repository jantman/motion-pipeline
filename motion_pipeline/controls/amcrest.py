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
from requests.auth import HTTPDigestAuth
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class Amcrest(object):

    def __init__(self, cam_name, base_url, user, passwd, timeout=10):
        self.cam_name = cam_name
        self._base_url = base_url
        self._user = user
        self._passwd = passwd
        self._timeout = timeout
        self._r = requests.Session()
        self._r.auth = HTTPDigestAuth(self._user, self._passwd)

    def _get(self, path):
        url = urljoin(self._base_url, path)
        logger.debug('%s - GET %s (path %s)', self.cam_name, url, path)
        r = self._r.get(url, timeout=self._timeout)
        r.raise_for_status()
        return r

    def _get_equals_lines(self, path):
        r = self._get(path)
        data = {}
        for line in r.text.strip().split('\n'):
            parts = line.strip().split('=')
            data[parts[0]] = parts[1]
        return data

    def _get_dumb(self, path):
        r = self._get(path)
        if r.text.strip() != 'OK':
            logger.error(
                'Got invalid response to Amcrest GET %s: %s',
                urljoin(self._base_url, path), r.text
            )
            raise RuntimeError(
                'Amcrest control of camera %s: '
                'Invalid response to GET %s: %s' %(
                    self.cam_name, urljoin(self._base_url, path), r.text
                )
            )
        return r

    @property
    def current_position(self):
        """
        Return the current camera position as an (X, Y) tuple of floats.

        :return: current position - X, Y floats
        :rtype: tuple
        """
        data = self._get_equals_lines(
            'cgi-bin/ptz.cgi?action=getStatus&channel=1'
        )
        pos = (
            float(data['status.Postion[0]']),
            float(data['status.Postion[1]'])
        )
        logger.info('Camera position: %s', pos)
        return pos

    def move(self, x, y):
        """
        Moves X units on the X axis and Y units on the Y axis. Note that as far
        as I can tell, these units are seemingly meaningless. They're clearly
        NOT the same units we get back when we request the position, even though
        they seem to be a similar scale.

        This is here because the firmware version for my cameras has the
        "PositionABS" (go to absolute position) command broken and it returns
        an error no matter what arguments are given.

        Suggested amounts to move are 1500 or 3000 at a time.

        :param x: number of units to move on the X axis; positive units move
          right and negative units move left
        :type x: float
        :param y: number of units to move on the Y axis; positive units move
          down and negative units move up
        :type y: float
        """
        url = '/cgi-bin/ptz.cgi?action=start&channel=1&code=Position&' \
              'arg1=%s&arg2=%s&arg3=0' % (x, y)
        logger.info('Moving camera by (%s, %s)', x, y)
        self._get_dumb(url)

    def move_to_preset(self, preset_num):
        url = '/cgi-bin/ptz.cgi?action=start&channel=1&code=GotoPreset&' \
              'arg1=0&arg2=%d&arg3=0' % preset_num
        logger.info(
            '%s: Moving camera to preset: %s', self.cam_name, preset_num
        )
        self._get_dumb(url)

    def set_preset_to_current(self, preset_num):
        url = '/cgi-bin/ptz.cgi?action=start&channel=1&code=SetPreset&' \
              'arg1=0&arg2=%d&arg3=0' % preset_num
        logger.info('%s: Setting preset: %d', self.cam_name, preset_num)
        self._get_dumb(url)
