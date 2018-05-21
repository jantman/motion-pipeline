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
from celery.utils.log import get_task_logger
from datetime import datetime

from motion_pipeline.database.db import init_db, db_session, cleanup_db
from motion_pipeline.database.models import Upload, MotionEvent
from motion_pipeline.motion_handler import FILE_UPLOAD_ACTIONS

logger = get_task_logger(__name__)

atexit.register(cleanup_db)
init_db()


class MotionTaskProcessor(object):
    """
    Class to process Celery tasks enqueued in response to ``motion`` events.
    """

    def __init__(self):
        pass

    def process(self, *args, **kwargs):
        logger.info('Picked up task: args=%s kwargs=%s', args, kwargs)
        if args[0] in FILE_UPLOAD_ACTIONS:
            self._handle_file_upload(**kwargs)
        elif args[0] == 'event_start':
            self._handle_event_start(**kwargs)
        elif args[0] == 'event_end':
            self._handle_event_end(**kwargs)
        elif args[0] == 'heartbeat':
            logger.warning('Ignoring heartbeat task: %s', kwargs)
        else:
            logger.error(
                'Discarding task with unknown action "%s": %s',
                args[0], kwargs
            )

    def _handle_event_start(self, **kwargs):
        logger.info('Writing event_start to DB')
        _date = datetime.strptime(
            kwargs['call_date'], '%Y-%m-%d %H:%M:%S'
        )
        db_session.add(MotionEvent(
            text_event=kwargs['text_event'],
            date=_date,
            event_id=kwargs['event_id'],
            frame_num=kwargs['frame_num'],
            cam_num=kwargs['cam'],
            changed_pixels=kwargs['changed_px'],
            noise=kwargs['noise'],
            motion_width=kwargs['motion_width'],
            motion_height=kwargs['motion_height'],
            motion_center_x=kwargs['motion_center_x'],
            motion_center_y=kwargs['motion_center_y'],
        ))
        db_session.commit()

    def _handle_event_end(self, **kwargs):
        e = db_session.query(MotionEvent).get(kwargs['text_event'])
        if e is not None:
            logger.debug(
                'Writing event_end to DB for existing event %s',
                kwargs['text_event']
            )
            e.is_finished = True
            db_session.commit()
            return
        # else we have an event_end without a matching event_start
        logger.debug(
            'Writing event_end to DB without matching started event '
            '(text_event=%s)', kwargs['text_event']
        )
        _date = datetime.strptime(
            kwargs['call_date'], '%Y-%m-%d %H:%M:%S'
        )
        e = MotionEvent(
            text_event=kwargs['text_event'],
            date=_date,
            event_id=kwargs['event_id'],
            frame_num=kwargs['frame_num'],
            cam_num=kwargs['cam'],
            changed_pixels=kwargs['changed_px'],
            noise=kwargs['noise'],
            motion_width=kwargs['motion_width'],
            motion_height=kwargs['motion_height'],
            motion_center_x=kwargs['motion_center_x'],
            motion_center_y=kwargs['motion_center_y'],
            is_finished=True
        )
        db_session.add(e)
        db_session.commit()

    def _handle_file_upload(self, **kwargs):
        logger.debug(
            'Writing file upload to DB; filename=%s', kwargs['filename']
        )
        _date = datetime.strptime(
            kwargs['call_date'], '%Y-%m-%d %H:%M:%S'
        )
        db_session.add(Upload(
            filename=os.path.basename(kwargs['filename']),
            date=_date,
            event_id=kwargs['event_id'],
            frame_num=kwargs['frame_num'],
            cam_num=kwargs['cam'],
            changed_pixels=kwargs['changed_px'],
            noise=kwargs['noise'],
            text_event=kwargs['text_event'],
            motion_width=kwargs['motion_width'],
            motion_height=kwargs['motion_height'],
            motion_center_x=kwargs['motion_center_x'],
            motion_center_y=kwargs['motion_center_y'],
            file_type=kwargs['filetype']
        ))
        db_session.commit()
