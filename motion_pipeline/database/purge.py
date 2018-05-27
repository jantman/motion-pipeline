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

import argparse
import logging
from botocore.exceptions import ClientError
from datetime import timedelta

from sqlalchemy import or_

from motion_pipeline.database.db import init_db, db_session
from motion_pipeline.cliutils import set_log_debug, set_log_info
from motion_pipeline.database.models import Video, MotionEvent, Notification
import motion_pipeline.settings as settings
from motion_pipeline.s3connection import get_s3_bucket
from motion_pipeline.utils import dtnow


logger = logging.getLogger(__name__)


def parse_args():
    p = argparse.ArgumentParser(
        description='Clean up archived recordings and database entries'
    )
    p.add_argument('-v', '--verbose', dest='verbose', action='count', default=0,
                   help='verbose output. specify twice for debug-level output.')
    args = p.parse_args()
    return args


def main():
    global logger
    logging.basicConfig(
        level=logging.WARNING,
        format="[%(asctime)s %(levelname)s] %(message)s"
    )
    logger = logging.getLogger()

    args = parse_args()

    # set logging level
    if args.verbose > 1:
        set_log_debug(logger)
    elif args.verbose == 1:
        set_log_info(logger)

    logger.info('Initializing DB...')
    init_db()
    logger.info('Done initializing database')
    run_database_cleanup()


def run_database_cleanup():
    purge_archived_from_db()
    purge_orphaned_events()


def purge_archived_from_db():
    bucket = get_s3_bucket(settings)
    archived = db_session.query(Video).filter(
        Video.is_archived.__eq__(True)
    ).all()
    logger.info(
        'Found %d archived videos in database', len(archived)
    )
    for video in archived:
        for n in db_session.query(Notification).filter(
            Notification.video_filename.__eq__(video.filename)
        ):
            db_session.delete(n)
        try:
            remove_bucket_object(
                bucket, settings.BUCKET_PREFIX + video.filename
            )
            if video.thumbnail_name is not None:
                remove_bucket_object(
                    bucket, settings.BUCKET_PREFIX + video.thumbnail_name
                )
        except Exception as ex:
            logger.error(
                'Excepting deleting archived video filename=%s: %s',
                video.filename, ex, exc_info=True
            )
            continue
        db_session.delete(video)
        db_session.delete(video.event)
        db_session.commit()


def remove_bucket_object(bucket, key):
    obj = bucket.Object(key)
    try:
        obj.content_length
    except ClientError as ex:
        if ex.response.get('Error', {}).get('Code', '0') == '404':
            logger.info('Object %s already deleted', key)
            return
        raise
    logger.info('Deleting Object %s', key)
    obj.delete()
    obj.wait_until_not_exists()


def purge_orphaned_events():
    orphaned = db_session.query(MotionEvent).filter(
        MotionEvent.video.__eq__(None),
        MotionEvent.date.__lt__(dtnow() - timedelta(days=1))
    ).all()
    logger.info(
        'Found %d events older than one day with no video', len(orphaned)
    )
    for e in orphaned:
        db_session.delete(e)
        db_session.commit()


if __name__ == "__main__":
    main()
