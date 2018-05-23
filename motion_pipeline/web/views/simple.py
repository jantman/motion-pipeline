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
from flask import render_template, send_from_directory, redirect, request

from sqlalchemy import asc

from motion_pipeline.web.app import app
from motion_pipeline.web.utils import proxy_aware_redirect
from motion_pipeline.database.db import db_session
from motion_pipeline.database.models import Upload, MotionEvent
from motion_pipeline import settings

logger = logging.getLogger(__name__)


class SimpleMainView(MethodView):
    """
    Render the GET /simple/ view using the ``index.html`` template.
    """

    def get(self):
        return render_template(
            'index.html'
        )


class SimpleLiveView(MethodView):
    """
    Render the GET /simple/live view using the ``live.html`` template.
    """

    def get(self):
        return render_template(
            'live.html'
        )


class SimpleVideosView(MethodView):
    """
    Render the GET /simple/videos view using the ``videos.html`` template.
    """

    def get(self):
        events = db_session.query(
            MotionEvent
        ).filter(
            MotionEvent.upload.has(is_archived=False)
        ).order_by(asc(MotionEvent.date)).all()
        return render_template(
            'videos.html', events=events
        )


class SimpleOneVideoView(MethodView):
    """
    Render the GET /simple/videos/<filename> view using the
    ``video.html`` template.
    """

    def get(self, video_filename):
        file = db_session.query(Upload).get(video_filename)
        return render_template(
            'video.html', upload=file
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
        upload = db_session.query(Upload).get(path)
        assert upload is not None
        logger.info('Archiving: %s', path)
        upload.is_archived = True
        db_session.commit()
        return proxy_aware_redirect('/simple/videos', code=302)


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
    '/simple/videos/<path:video_filename>',
    view_func=SimpleOneVideoView.as_view('simple_one_video_view')
)
app.add_url_rule(
    '/uploads/<path:path>', view_func=UploadsView.as_view('uploads_view')
)
app.add_url_rule(
    '/simple/archive/<path:path>', view_func=ArchiveView.as_view('archive_view')
)
