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

function loadDetectionStatus() {
    $.ajax({
        url: '/api/detection/status',
        success: function(data) {
            Object.keys(data).forEach(function (key) {
                var state = data[key];
                var elem = $('#detection_status_' + key);
                if(state == "ACTIVE") {
                    elem.html('<a href="#" onclick="setDetection(\'' + key + '\', \'0\')">ACTIVE</a>');
                    elem.removeClass('unknown paused');
                    elem.addClass('active');
                } else if (state == "PAUSE") {
                    elem.html('<a href="#" onclick="setDetection(\'' + key + '\', \'1\')">PAUSED</a>');
                    elem.removeClass('active unknown');
                    elem.addClass('paused');
                } else {
                    elem.html('<a href="#" onclick="">UNKNOWN</a>');
                    elem.removeClass('active paused');
                    elem.addClass('unknown');
                }
            });
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log('loadDetectionStatus() error: %s (%s)', textStatus, errorThrown);
            alert('ERROR: loadDetectionStatus() failed; see console log for details (and change this to a modal!)');
        }
    });
}

function setDetection(cam_name, state) {
    var url = '';
    if(state == 1) {
        url = '/api/detection/start';
    } else {
        url = '/api/detection/pause';
    }
    if(cam_name != null) {
        url = url + '?cam=' + cam_name;
    }
    $.ajax({
        url: url,
        success: function(data) {
            if(! data.hasOwnProperty('success') || data['success'] != true){
                console.log('setDetection(%s, %s) error: %o', cam_name, state, data);
                alert('ERROR: setDetection() failed; see console log for details (and change this to a modal!)');
            } else {
                loadDetectionStatus();
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log('setDetection(%s, %s) error: %s (%s)', cam_name, state, textStatus, errorThrown);
            alert('ERROR: setDetection() failed; see console log for details (and change this to a modal!)');
        }
    });
}
