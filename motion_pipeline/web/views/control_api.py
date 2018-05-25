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
from motion_pipeline.controls import CONTROL_CLASSES

logger = logging.getLogger(__name__)


def control_for_camera(cam_name):
    data = settings.CAMERAS[cam_name]
    assert data['control_info'] is not None
    cls = CONTROL_CLASSES[data['control_info']['control_type']]
    return cls(
        cam_name,
        data['control_info']['control_base_url'],
        data['control_info']['control_user'],
        data['control_info']['control_pass'],
        timeout=2
    )


class MoveCamera(MethodView):
    """
    Render the GET /api/control/<string:cam_name>/move API response.

    Query Parameters:
    x - float
    y - float
    """

    def get(self, cam_name):
        raise NotImplementedError('disable detection first!')
        ctrl = control_for_camera(cam_name)
        x = float(request.args.get('x', '0.0'))
        y = float(request.args.get('y', '0.0'))
        logger.info(
            'Request to move camera %s by x=%s y=%s',
            cam_name, x, y
        )
        ctrl.move(x, y)
        return jsonify({'success': True})


class MoveCameraToPreset(MethodView):
    """
    Render the GET /api/control/<string:cam_name>/move_to_preset API response.

    Query Parameters:
    preset - int
    """

    def get(self, cam_name):
        raise NotImplementedError('disable detection first!')
        ctrl = control_for_camera(cam_name)
        preset_num = int(request.args['preset'])
        logger.info(
            'Request to move camera %s to preset %d',
            cam_name, preset_num
        )
        ctrl.move_to_preset(preset_num)
        return jsonify({'success': True})


class SetPreset(MethodView):
    """
    Render the GET /api/control/<string:cam_name>/set_preset API response.

    Query Parameters:
    preset - int
    """

    def get(self, cam_name):
        ctrl = control_for_camera(cam_name)
        preset_num = int(request.args['preset'])
        logger.info(
            'Request to set camera %s preset %d',
            cam_name, preset_num
        )
        ctrl.set_preset_to_current(preset_num)
        return jsonify({'success': True})


app.add_url_rule(
    '/api/control/<string:cam_name>/move',
    view_func=MoveCamera.as_view('control_move_camera')
)
app.add_url_rule(
    '/api/control/<string:cam_name>/move_to_preset',
    view_func=MoveCameraToPreset.as_view('control_move_to_preset')
)
app.add_url_rule(
    '/api/control/<string:cam_name>/set_preset',
    view_func=SetPreset.as_view('control_set_preset')
)
