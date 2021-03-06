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
from subprocess import run, PIPE, STDOUT
from decimal import Decimal, ROUND_UP

from celery.utils.log import get_task_logger
from PIL import Image

import motion_pipeline.settings as settings
from motion_pipeline.database.db import db_session, cleanup_db
from motion_pipeline.database.models import Video, MotionEvent, FrameDebugInfo
from motion_pipeline.handler_actions import FILE_UPLOAD_ACTIONS
from motion_pipeline.utils import autoremoving_tempfile
from motion_pipeline.s3connection import get_s3_bucket

try:
    from anyjson import deserialize
except ImportError:
    from json import loads as deserialize

logger = get_task_logger(__name__)

atexit.register(cleanup_db)


class MotionTaskProcessor(object):
    """
    Class to process Celery tasks enqueued in response to ``motion`` events.
    """

    def __init__(self, tasklogger=None):
        global logger
        if tasklogger is not None:
            logger = tasklogger
        db_session.expire_all()

    def process(self, *args, **kwargs):
        logger.info('Picked up task: args=%s kwargs=%s', args, kwargs)
        try:
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
        finally:
            db_session.expunge_all()
            cleanup_db()

    def _handle_event_start(self, **kwargs):
        logger.info('Writing event_start to DB')
        _date = datetime.strptime(
            kwargs['call_date'], '%Y-%m-%d %H:%M:%S'
        )
        _call_date = datetime.strptime(
            kwargs['handler_call_time'], '%Y-%m-%d %H:%M:%S'
        )
        db_session.add(MotionEvent(
            text_event=kwargs['text_event'],
            date=_date,
            event_id=kwargs['event_id'],
            frame_num=kwargs['frame_num'],
            cam_num=kwargs['cam'],
            cam_name=kwargs['cam_name'],
            host=kwargs['host'],
            changed_pixels=kwargs['changed_px'],
            threshold=kwargs['threshold'],
            despeckle_labels=kwargs['despeckle_labels'],
            fps=kwargs['fps'],
            noise=kwargs['noise'],
            motion_width=kwargs['motion_width'],
            motion_height=kwargs['motion_height'],
            motion_center_x=kwargs['motion_center_x'],
            motion_center_y=kwargs['motion_center_y'],
            handler_call_start_datetime=_call_date
        ))
        db_session.commit()
        from motion_pipeline.celerytasks.tasks import newevent_ready
        newevent_ready.delay(kwargs['text_event'])

    def _handle_event_end(self, **kwargs):
        e = db_session.query(MotionEvent).get(kwargs['text_event'])
        _call_date = datetime.strptime(
            kwargs['handler_call_time'], '%Y-%m-%d %H:%M:%S'
        )
        if e is None:
            logger.info(
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
                cam_name=kwargs['cam_name'],
                host=kwargs['host'],
                changed_pixels=kwargs['changed_px'],
                threshold=kwargs['threshold'],
                despeckle_labels=kwargs['despeckle_labels'],
                fps=kwargs['fps'],
                noise=kwargs['noise'],
                motion_width=kwargs['motion_width'],
                motion_height=kwargs['motion_height'],
                motion_center_x=kwargs['motion_center_x'],
                motion_center_y=kwargs['motion_center_y']
            )
            db_session.add(e)
        else:
            logger.info(
                'Writing event_end to DB for existing event %s',
                kwargs['text_event']
            )
        e.is_finished = True
        e.handler_call_end_datetime = _call_date
        if kwargs.get('debug_frame_info', None) is not None:
            self._handle_debug_frame_info(
                kwargs['text_event'], kwargs['debug_frame_info']
            )
        db_session.commit()

    def _handle_debug_frame_info(self, text_event, infos):
        for i in infos:
            try:
                i['text_event'] = text_event
                d = i['date']
                i['date'] = datetime.strptime(d, '%Y-%m-%d %H:%M:%S')
                db_session.add(FrameDebugInfo(**i))
            except Exception:
                logger.error(
                    'Malformed debug_frame_info entry: %s', i, exc_info=True
                )

    def _handle_file_upload(self, **kwargs):
        logger.info(
            'Writing file upload to DB for filename: %s', kwargs['filename']
        )
        _date = datetime.strptime(
            kwargs['call_date'], '%Y-%m-%d %H:%M:%S'
        )
        _call_date = datetime.strptime(
            kwargs['handler_call_time'], '%Y-%m-%d %H:%M:%S'
        )
        db_session.add(Video(
            filename=os.path.basename(kwargs['filename']),
            date=_date,
            event_id=kwargs['event_id'],
            cam_num=kwargs['cam'],
            cam_name=kwargs['cam_name'],
            host=kwargs['host'],
            text_event=kwargs['text_event'],
            file_type=kwargs['filetype'],
            threshold=kwargs['threshold'],
            despeckle_labels=kwargs['despeckle_labels'],
            fps=kwargs['fps'],
            handler_call_datetime=_call_date
        ))
        db_session.commit()
        from motion_pipeline.celerytasks.tasks import do_thumbnail
        do_thumbnail.delay(os.path.basename(kwargs['filename']))

    def create_and_upload_thumbnail(
            self, filename, trigger_newvideo_ready=True
    ):
        if settings.MINIO_LOCAL_MOUNTPOINT is None:
            raise NotImplementedError(
                'ERROR: Downloading new videos from S3 not yet implemented!'
            )
        video = db_session.query(Video).get(filename)
        assert video is not None
        s3 = get_s3_bucket(settings, tasklogger=logger)
        vid_path = os.path.join(settings.MINIO_LOCAL_MOUNTPOINT, filename)
        logger.debug('Handling new video at: %s', vid_path)
        thumbnail_name = '%s.jpg' % filename
        logger.info('Generating still thumbnail of second frame of %s to: %s',
                    filename, thumbnail_name)
        video_length = None
        with autoremoving_tempfile(suffix='.jpg') as imgpath:
            with autoremoving_tempfile(suffix='.jpg') as framepath:
                # get the length of the video
                cmd = [
                    'ffprobe', '-show_format', '-of', 'json', '-i', vid_path
                ]
                logger.debug('Running: %s', ' '.join(cmd))
                res = run(cmd, stdout=PIPE, timeout=120)
                ffprobe_json = deserialize(res.stdout.strip().decode())
                logger.debug(
                    'ffprobe JSON lists video duration as: %s',
                    ffprobe_json['format']['duration']
                )
                video_length = Decimal(
                    ffprobe_json['format']['duration']
                ).quantize(Decimal('.001'), rounding=ROUND_UP)
                # Extract the second frame from the video
                cmd = [
                    'ffmpeg', '-y', '-ss', '00:00:00.2',
                    '-i', vid_path, '-frames:v', '1', framepath
                ]
                logger.debug('Running: %s', ' '.join(cmd))
                res = run(cmd, stdout=PIPE, stderr=STDOUT, timeout=120)
                if res.returncode != 0:
                    raise RuntimeError(
                        'ERROR: ffmpeg command "%s" exited %d:\n%s' % (
                            ' '.join(cmd), res.returncode, res.stdout
                        )
                    )
                fsize = os.stat(framepath).st_size
                if fsize < 100:
                    raise RuntimeError(
                        'ERROR: ffmpeg command "%s" resulted in %d '
                        'byte file:\n%s',
                        ' '.join(cmd), fsize, res.stdout
                    )
                logger.debug('ffmpeg complete; %d-byte file', fsize)
                # create a thumbnail from that
                logger.debug('Creating thumbnail of still...')
                i = Image.open(framepath)
                i.thumbnail(settings.THUMBNAIL_MAX_SIZE, Image.ANTIALIAS)
                i.save(imgpath, 'JPEG')
                key = '%s%s' % (settings.BUCKET_PREFIX, thumbnail_name)
                logger.debug('Uploading thumbnail to S3 at: %s', key)
                s3.upload_file(imgpath, key)
        logger.info(
            'Still thumbnail of %s uploaded to S3 at: %s', filename, key
        )
        # update the DB with the thumbnail name
        video.thumbnail_name = thumbnail_name
        video.length_sec = video_length
        db_session.commit()
        if trigger_newvideo_ready:
            from motion_pipeline.celerytasks.tasks import newvideo_ready
            newvideo_ready.delay(video.filename, video.text_event)
        db_session.expunge_all()
        cleanup_db()
