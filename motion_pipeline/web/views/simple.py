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
from flask import render_template, send_from_directory, request
from copy import deepcopy

from sqlalchemy import asc, func

from motion_pipeline.web.app import app
from motion_pipeline.web.utils import proxy_aware_redirect
from motion_pipeline.database.db import db_session
from motion_pipeline.database.models import (
    Video, MotionEvent, Notification, EventDispositionEnum
)
from motion_pipeline.database.dbsettings import get_db_setting
from motion_pipeline import settings

logger = logging.getLogger(__name__)


def cams_dict():
    cams = {
        x: deepcopy(settings.CAMERAS[x]) for x in settings.CAMERAS.keys()
    }
    for cname in cams.keys():
        levt = db_session.query(MotionEvent).filter(
            MotionEvent.cam_name.__eq__(cname)
        ).order_by(MotionEvent.date.desc()).first()
        cams[cname]['latest_event'] = levt
        lvideo = db_session.query(Video).filter(
            Video.cam_name.__eq__(cname)
        ).order_by(Video.date.desc()).first()
        cams[cname]['latest_video'] = lvideo
    return cams


class SimpleMainView(MethodView):
    """
    Render the GET /simple/ view using the ``index.html`` template.
    """

    def get(self):
        unseen_count = db_session.query(
            Video.filename
        ).filter(
            Video.is_archived.__eq__(False)
        ).count()
        return render_template(
            'index.html', unseen_count=unseen_count,
            notifications_enabled=get_db_setting('notifications', True)
        )


class SimpleLiveView(MethodView):
    """
    Render the GET /simple/live view using the ``live.html`` template.
    """

    def get(self):
        unseen_counts = {
            x[0]: x[1] for x in
            db_session.query(
                Video.cam_name, func.count(Video.cam_name)
            ).filter(
                Video.is_archived.__eq__(False)
            ).group_by(Video.cam_name).all()
        }
        cams = cams_dict()
        for camname in cams.keys():
            logger.info(
                'cam %s latest_event: %s',
                camname, cams[camname]['latest_event']
            )
        return render_template(
            'live.html', unseen_count=sum(unseen_counts.values()),
            new_video_counts=unseen_counts, cameras=cams,
            cam_names=sorted(settings.CAMERAS.keys()),
            notifications_enabled=get_db_setting('notifications', True)
        )


class SimpleVideosView(MethodView):
    """
    Render the GET /simple/videos view using the ``videos.html`` template.
    """

    def get(self):
        filters = [
            MotionEvent.video.has(is_archived=False),
            MotionEvent.video.__ne__(None)
        ]
        dispo = None
        if 'dispo' in request.args:
            dispo = request.args['dispo']
            if dispo == 'none':
                filters.append(
                    MotionEvent.disposition.__eq__(None)
                )
            else:
                filters.append(
                    MotionEvent.disposition.__eq__(
                        EventDispositionEnum[dispo]
                    )
                )
        events = db_session.query(
            MotionEvent
        ).filter(*filters).order_by(asc(MotionEvent.date)).all()
        unseen_count = db_session.query(
            Video.filename
        ).filter(
            Video.is_archived.__eq__(False)
        ).count()
        cams = cams_dict()
        return_to = '/simple/videos'
        if dispo is not None:
            return_to += '?dispo=%s' % dispo
        return render_template(
            'videos.html', events=events, unseen_count=unseen_count,
            cameras=cams, cam_names=sorted(settings.CAMERAS.keys()),
            notifications_enabled=get_db_setting('notifications', True),
            dispo_enum=EventDispositionEnum, dispo=dispo, return_to=return_to
        )


class SimpleOneVideoView(MethodView):
    """
    Render the GET /simple/videos/<filename> view using the
    ``video.html`` template.
    """

    def get(self, video_filename):
        file = db_session.query(Video).get(video_filename)
        cams = cams_dict()
        return_to = request.args.get('return_to', '/simple/videos')
        return render_template(
            'video.html', video=file, cameras=cams,
            cam_names=sorted(settings.CAMERAS.keys()),
            notifications_enabled=get_db_setting('notifications', True),
            return_to=return_to
        )


class UploadsView(MethodView):
    """
    Serve the uploads.
    """

    def get(self, path):
        return send_from_directory(settings.MINIO_LOCAL_MOUNTPOINT, path)


class ArchiveView(MethodView):
    """
    Archive a video
    """

    def get(self, path):
        return_to = request.args.get('return_to', '/simple/videos')
        upload = db_session.query(Video).get(path)
        assert upload is not None
        logger.info('Archiving: %s', path)
        upload.is_archived = True
        db_session.commit()
        return proxy_aware_redirect(return_to, code=302)


class SetDispositionHandler(MethodView):
    """
    Set the disposition on an event
    """

    def post(self, text_event):
        event = db_session.query(MotionEvent).get(text_event)
        assert event is not None
        m = request.get_json()
        if m is None:
            m = request.get_data()
        logger.info(
            'Setting disposition of event %s to: %s',
            text_event, m['disposition']
        )
        if m['disposition'] == 'none':
            event.disposition = None
        else:
            event.disposition = EventDispositionEnum[m['disposition']]
        db_session.commit()
        return 'OK'


class NotificationRedirect(MethodView):
    """
    Redirect for a notification
    """

    def get(self, _id):
        n = db_session.query(Notification).get(_id)
        assert n is not None
        return proxy_aware_redirect(
            '/simple/videos/%s.htm' % n.video_filename,
            code=302
        )


class ClientLog(MethodView):

    def post(self):
        m = request.get_json()
        if m is None:
            m = request.get_data()
        self._log(m)
        return 'OK'

    def get(self):
        self._log(dict(request.args))
        return 'OK'

    def _log(self, data):
        logger.info(
            'ClientLog from %s (%s): %s', request.environ['REMOTE_ADDR'],
            request.environ['HTTP_USER_AGENT'], data
        )


app.add_url_rule(
    '/simple/', view_func=SimpleMainView.as_view('simple_main_view')
)
app.add_url_rule(
    '/simple/live', view_func=SimpleLiveView.as_view('simple_live_view')
)
app.add_url_rule(
    '/simple/videos', view_func=SimpleVideosView.as_view('simple_videos_view')
)
app.add_url_rule(
    '/simple/videos/<path:video_filename>.htm',
    view_func=SimpleOneVideoView.as_view('simple_one_video_view')
)
app.add_url_rule(
    '/uploads/<path:path>', view_func=UploadsView.as_view('uploads_view')
)
app.add_url_rule(
    '/simple/archive/<path:path>.htm', view_func=ArchiveView.as_view('archive_view')
)
app.add_url_rule(
    '/simple/setDisposition/<path:text_event>.htm',
    view_func=SetDispositionHandler.as_view('set_disposition_view')
)
app.add_url_rule(
    '/simple/clientlog', view_func=ClientLog.as_view('client_log')
)
app.add_url_rule(
    '/simple/n/<int:_id>',
    view_func=NotificationRedirect.as_view('notification_redirect')
)
