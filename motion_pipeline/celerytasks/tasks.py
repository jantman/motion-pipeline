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

# !!! IMPORTANT !!! - This module will also be imported in motion_handler.py
# and the web components. Imports here should be as minimal as possible, with
# most imports in motion_pipeline.celerytasks.processor

from celery.utils.log import get_task_logger

from motion_pipeline.celerytasks.celeryapp import app

logger = get_task_logger(__name__)


@app.task(
    bind=True, name='motion_ingest', max_retries=4, acks_late=True,
    task_time_limit=30
)
def motion_ingest(self, *args, **kwargs):
    """
    Task to ingest new events or pictures/movies from motion.
    """
    logger.debug(
        'Running task motion_ingest() id=%s retries=%d args=%s kwargs=%s',
        self.request.id, self.request.retries, args, kwargs
    )
    try:
        from motion_pipeline.celerytasks.processor import MotionTaskProcessor
        kwargs['retries'] = self.request.retries
        MotionTaskProcessor(logger).process(*args, **kwargs)
        logger.debug('Task %s complete.', self.request.id)
    except Exception as ex:
        logger.warning(
            'Caught exception running task with args=%s kwargs=%s: %s' % (
                args, kwargs, ex
            ), exc_info=True
        )
        self.retry(countdown=2 ** self.request.retries)
