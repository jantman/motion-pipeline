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
from flask.views import MethodView
from flask import jsonify, request

from motion_pipeline.web.app import app
from motion_pipeline import settings
from motion_pipeline.motionapi import MotionApi, MotionApiException
from motion_pipeline.web.simplecache import SimpleCache

logger = logging.getLogger(__name__)


def get_motion_apis():
    res = {}
    for cam_name, data in settings.CAMERAS.items():
        res[cam_name] = MotionApi(
            data['motion_host'], data['motion_port'], data['motion_camera_id'],
            cam_name
        )
    return res


def get_detection_status(cache=True):
    cachekey = 'detectionstatus'
    sc = SimpleCache(
        settings.REDIS_BROKER_URL, settings.SIMPLECACHE_KEY_PREFIX
    )
    if cache:
        c = sc.hash_get(cachekey)
        if c != {}:
            logger.debug('Using cached detectionstatus value: %s', c)
            return c
    cams = get_motion_apis()
    res = {}
    for cam_name, api in cams.items():
        try:
            res[cam_name] = api.detection_status
        except MotionApiException as ex:
            logger.error(
                'Error getting detection status of camera %s: %s',
                cam_name, ex, exc_info=True
            )
            res[cam_name] = 'unknown'
    sc.hash_set(cachekey, res, ttl=30)
    return res


class DetectionStatus(MethodView):
    """
    Render the GET /api/detection/status API response.
    """

    def get(self):
        return jsonify(get_detection_status())


class DetectionStart(MethodView):
    """
    Render the GET /api/detection/start API response.
    """

    def get(self):
        cams = get_motion_apis()
        cam_names = cams.keys()
        if 'cam' in request.args:
            cam_names = [request.args.get('cam')]
        for cam_name in cam_names:
            cams[cam_name].resume_detection()
        # bust cache on detection status
        get_detection_status(cache=False)
        return jsonify({'success': True})


class DetectionPause(MethodView):
    """
    Render the GET /api/detection/pause API response.
    """

    def get(self):
        cams = get_motion_apis()
        cam_names = cams.keys()
        if 'cam' in request.args:
            cam_names = [request.args.get('cam')]
        for cam_name in cam_names:
            cams[cam_name].pause_detection()
        # bust cache on detection status
        get_detection_status(cache=False)
        return jsonify({'success': True})


app.add_url_rule(
    '/api/detection/status',
    view_func=DetectionStatus.as_view('detection_status')
)
app.add_url_rule(
    '/api/detection/start',
    view_func=DetectionStart.as_view('detection_start')
)
app.add_url_rule(
    '/api/detection/pause',
    view_func=DetectionPause.as_view('detection_pause')
)
