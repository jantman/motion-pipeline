/*
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
 */

function moveCameraBy(cam_name, x, y) {
    var url = '/api/control/' + cam_name + '/move?x=' + x + '&y=' + y;
    $.ajax({
        url: url,
        error: function(jqXHR, textStatus, errorThrown) {
            console.log('moveCameraBy(%s, %s, %s) error: %s (%s)', cam_name, x, y, textStatus, errorThrown);
            alert('ERROR: moveCameraBy() failed; see console log for details (and change this to a modal!)');
        }
    });
}

function moveCameraToPreset(cam_name, preset_num) {
    var url = '/api/control/' + cam_name + '/move_to_preset?preset=' + preset_num;
    $.ajax({
        url: url,
        error: function(jqXHR, textStatus, errorThrown) {
            console.log('moveCameraToPreset(%s, %s) error: %s (%s)', cam_name, preset_num, textStatus, errorThrown);
            alert('ERROR: moveCameraToPreset() failed; see console log for details (and change this to a modal!)');
        }
    });
}

function setCameraPreset(cam_name, preset_num) {
    var url = '/api/control/' + cam_name + '/set_preset?preset=' + preset_num;
    $.ajax({
        url: url,
        error: function(jqXHR, textStatus, errorThrown) {
            console.log('setCameraPreset(%s, %s) error: %s (%s)', cam_name, preset_num, textStatus, errorThrown);
            alert('ERROR: setCameraPreset() failed; see console log for details (and change this to a modal!)');
        }
    });
}
