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
import atexit
from datetime import datetime
import requests
import time

from celery.utils.log import get_task_logger

import motion_pipeline.settings as settings
from motion_pipeline.database.db import db_session, cleanup_db
from motion_pipeline.database.models import Notification, Video, MotionEvent

logger = get_task_logger(__name__)

atexit.register(cleanup_db)


class NotificationProcessor(object):
    """
    Class to process Celery tasks to create notifications.
    """

    def __init__(
        self, filename, event_text, celery_request, notification_id=None,
        tasklogger=None
    ):
        global logger
        if tasklogger is not None:
            logger = tasklogger
        db_session.expire_all()
        logger.debug(
            'Initalizing NotificationProcessor filename=%s event_text=%s '
            'notification_id=%s', filename, event_text, notification_id
        )
        self._celery_request = celery_request
        self._filename = filename
        self._event_text = event_text
        self._notification = self._get_notification_from_db(notification_id)
        self._video = db_session.query(Video).get(filename)
        self._event = db_session.query(MotionEvent).get(event_text)
        logger.debug('video=%s event=%s', self._video, self._event)
        assert self._video.event == self._event
        assert self._event.video == self._video
        assert self._video is not None
        assert settings.MINIO_LOCAL_MOUNTPOINT is not None

    def _get_notification_from_db(self, notification_id):
        if notification_id is not None:
            n = db_session.query(Notification).get(notification_id)
            if n is not None:
                logger.debug('Found existing Notification with ID %s', n.id)
                return n
        logger.debug('Generating new Notification in DB')
        n = Notification(
            video_filename=self._filename,
            text_event=self._event_text,
            generated_time=datetime.now(),
            provider_name='pushover'
        )
        db_session.add(n)
        db_session.commit()
        return n

    @property
    def notification_id(self):
        return self._notification.id

    def generate(self):
        """generate params for the POST to pushover"""
        logger.debug('Generating parameters for notification...')
        thumb_path = os.path.join(
            settings.MINIO_LOCAL_MOUNTPOINT, self._video.thumbnail_name
        )
        d = {
            'data': {
                'token': settings.PUSHOVER_API_KEY,
                'user': settings.PUSHOVER_USER_KEY,
                'title': 'Motion Detected on %s' % self._event.cam_name,
                'message': 'Motion detected; %d pixels changed; video length '
                           '%.2f seconds' % (
                               self._event.changed_pixels,
                               self._video.length_sec
                           ),
                'timestamp': time.mktime(self._event.date.timetuple())
            },
            'files': {
                'attachment': (
                    self._video.thumbnail_name,
                    open(thumb_path, 'rb'),
                    'image/jpeg'
                )
            }
        }
        d['data']['url'] = '%ssimple/n/%d' % (
            settings.NOTIFICATION_BASE_URL, self._notification.id
        )
        if settings.PUSHOVER_SEND_EMERGENCY or settings.PUSHOVER_RETRY:
            d['data']['retry'] = 300  # 5 minutes
        if settings.PUSHOVER_SEND_EMERGENCY:
            d['data']['priority'] = 2
            d['data']['expire'] = 10800  # 3 hours - max
        return d

    def send(self, params):
        """send to pushover"""
        logger.debug('Sending Pushover notification; params=%s', params)
        r = requests.post('https://api.pushover.net/1/messages.json', **params)
        logger.debug(
            'Pushover POST response HTTP %s: %s', r.status_code, r.text
        )
        r.raise_for_status()
        if r.json()['status'] != 1:
            raise RuntimeError('Error response from Pushover: %s', r.text)
        self._notification.sent_time = datetime.now()
        self._notification.num_retries = self._celery_request.retries
        self._notification.provider_response = r.text
        db_session.commit()
        db_session.expunge_all()
        cleanup_db()

    def generate_and_send(self):
        """generate params and POST to pushover"""
        self.send(self.generate())
