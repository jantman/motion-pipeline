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

function loadNotificationStatus() {
    $.ajax({
        url: '/api/notifications/state',
        success: function(data) {
            var elem = $('#notificationStatus');
            if(data.state === true){
                elem.html('<a href="#" onclick="setNotifications(0)">ACTIVE</a>');
                elem.removeClass('unknown paused');
                elem.addClass('active');
            } else if (data.state === false) {
                elem.html('<a href="#" onclick="setNotifications(1)">DISABLED</a>');
                elem.removeClass('active unknown');
                elem.addClass('paused');
            } else {
                elem.html('<a href="#" onclick="">UNKNOWN</a>');
                elem.removeClass('active paused');
                elem.addClass('unknown');
                console.log('loadNotificationStatus() got invalid response: %s', data);
                alert('ERROR: loadNotificationStatus() got invalid response; see console log for details (and change this to a modal!)');
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log('loadDetectionStatus() error: %s (%s)', textStatus, errorThrown);
            alert('ERROR: loadDetectionStatus() failed; see console log for details (and change this to a modal!)');
        }
    });
}

function setNotifications(state) {
    var setState;
    if(state == 0) {
        setState = false;
    } else if(state == 1) {
        setState = true;
    } else {
        console.log('setNotifications(' + state + ') - invalid state!');
        alert('Invalid state for notifications;  see console log for details (and change this to a modal!)');
    }
    $.ajax({
        url: '/api/notifications/state',
        method: 'POST',
        data: JSON.stringify({'state': setState}),
        dataType: 'json',
        contentType: "application/json; charset=utf-8",
        success: function(data) {
            if(data.success === true) {
                loadNotificationStatus();
            } else {
                console.log('setNotifications() error: %s', data);
                alert('ERROR: setNotifications() failed; see console log for details (and change this to a modal!)');
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log('setNotifications() error: %s (%s)', textStatus, errorThrown);
            alert('ERROR: setNotifications() failed; see console log for details (and change this to a modal!)');
        }
    });
}
