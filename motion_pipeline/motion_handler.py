#!/usr/bin/env python3
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

import sys
import argparse
import logging
from datetime import datetime
import time
import os
import psutil
import importlib

try:
    from anyjson import serialize
    from anyjson import deserialize
except ImportError:
    from json import dumps as serialize
    from json import loads as deserialize

from motion_pipeline.handler_actions import KNOWN_ACTIONS, FILE_UPLOAD_ACTIONS

# imported in main, after daemonization
logger = None
settings = None
motion_ingest = None
get_s3_bucket = None
boto3 = None

START_TIME = time.time()


def sizeof_fmt(num):
    """Readable file size
    :param num: Bytes value
    :type num: int
    :rtype: str
    """
    for unit in ['', 'k', 'M', 'G', 'T']:
        if abs(num) < 1024.0:
            return "%3.1f %sB" % (num, unit)
        num /= 1024.0
    return "%.1f%s" % (num, 'P')


class MotionHandler(object):

    def __init__(self):
        self._bucket = get_s3_bucket(settings)

    def run(self, action, args_dict):
        logger.debug('run() action=%s args=%s', action, args_dict)
        if action not in FILE_UPLOAD_ACTIONS:
            logger.debug('Enqueueing Celery task...')
            motion_ingest.delay(action, **args_dict)
            logger.debug('No file upload; run finished.')
            return
        logger.debug('Finding bucket')
        logger.debug('Got bucket')
        for attempt in range(0, settings.HANDLER_MAX_UPLOAD_ATTEMPTS):
            try:
                self.upload_file(args_dict)
                logger.debug('Enqueueing Celery task for file upload...')
                motion_ingest.delay(action, **args_dict)
                os.unlink(args_dict['filename'])
                logger.debug('Deleted: %s', args_dict['filename'])
                return
            except Exception:
                logger.error(
                    'Error uploading file on try %d; sleep 5s', attempt,
                    exc_info=True
                )
                time.sleep(5)
        else:
            raise RuntimeError('ERROR: All upload attempts failed.')

    def upload_file(self, args):
        assert args['filename'] is not None
        obj_key = settings.BUCKET_PREFIX + os.path.basename(args['filename'])
        size_b = os.stat(args['filename']).st_size
        fsize = sizeof_fmt(size_b)
        txfrConf=boto3.s3.transfer.TransferConfig(use_threads=False)
        logger.debug(
            'Uploading %s file from %s to %s', fsize, args['filename'], obj_key
        )
        start_time = time.time()
        self._bucket.upload_file(
            args['filename'], obj_key,
            ExtraArgs={
                'ACL': 'private',
                'Metadata': {
                    'size_b': '%s' % size_b
                }
            },
            Config=txfrConf
        )
        end_time = time.time()
        logger.info(
            'Uploaded %s file to s3://%s/%s in %.4fs',
            fsize, self._bucket.name, obj_key, end_time - start_time
        )


def parse_args(argv):
    p = argparse.ArgumentParser(description='handler for Motion events')
    p.add_argument('-v', '--verbose', dest='verbose', action='count', default=0,
                   help='verbose output. specify twice for debug-level output.')
    p.add_argument('-f', '--foreground', dest='foreground', action='store_true',
                   default=False, help='log to foreground instead of file')
    p.add_argument('-c', '--config', dest='config', action='store', type=str,
                   default=None,
                   help='settings file path (MOTION_SETTINGS_PATH)')
    p.add_argument(
        '--action', dest='action', type=str, choices=KNOWN_ACTIONS,
        required=True,
        help='motion action/event; "dump-settings" will dump settings and exit'
    )
    p.add_argument('--cam', dest='cam_num', type=int, default=None)
    p.add_argument('--cam-name', dest='cam_name', type=str, default=None)
    p.add_argument('--changed_px', dest='changed_px', type=int, default=None)
    p.add_argument('--date', dest='call_date', type=str,
                   default=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    p.add_argument('--event_id', dest='event_id', type=int, default=None)
    p.add_argument('--filename', dest='filename', type=str, default=None)
    p.add_argument('--filetype', dest='filetype', type=int, default=None)
    p.add_argument('--frame_num', dest='frame_num', type=int, default=None)
    p.add_argument(
        '--motion_center_x', dest='motion_center_x', type=int, default=None
    )
    p.add_argument(
        '--motion_center_y', dest='motion_center_y', type=int, default=None
    )
    p.add_argument(
        '--motion_height', dest='motion_height', type=int, default=None
    )
    p.add_argument(
        '--motion_width', dest='motion_width', type=int, default=None
    )
    p.add_argument('--noise', dest='noise', type=int, default=None)
    p.add_argument('--text_event', dest='text_event', type=str, default=None)
    p.add_argument('--threshold', dest='threshold', type=int, default=None)
    p.add_argument('--labels', dest='despeckle_labels', type=int, default=None)
    p.add_argument('--fps', dest='fps', type=int, default=None)
    p.add_argument('--host', dest='host', type=str, default=None)
    args = p.parse_args(argv)
    return args


def get_basicconfig_kwargs(args):
    log_kwargs = {
        'level': logging.WARNING,
        'format': "[%(asctime)s %(levelname)s][%(process)d] %(message)s"
    }
    if not args.foreground:
        log_kwargs['filename'] = settings.HANDLER_LOG_PATH
    # set logging level
    if args.verbose > 1 or settings.HANDLER_LOG_DEBUG:
        log_kwargs['level'] = logging.DEBUG
        log_kwargs['format'] = "%(asctime)s [%(process)d - %(levelname)s " \
                               "%(filename)s:%(lineno)s - %(name)s." \
                               "%(funcName)s() ] %(message)s"
    elif args.verbose == 1 or settings.HANDLER_LOG_INFO:
        log_kwargs['level'] = logging.INFO
        log_kwargs['format'] = '%(asctime)s [%(process)d] %(levelname)s:' \
                               '%(name)s:%(message)s'
    return log_kwargs


def runcron():
    logger.info('Beginning cron-triggered run...')
    count = 0
    cutoff = time.time() - 60
    for f in os.listdir(settings.MOTION_SAVE_DIR):
        p = os.path.join(settings.MOTION_SAVE_DIR, f)
        if not os.path.isfile(p) or not p.endswith('.json'):
            continue
        if os.stat(p).st_mtime > cutoff:
            logger.info('Skipping file less than 60s old: %s', p)
            continue
        try:
            with open(p, 'r') as fh:
                args = deserialize(fh.read())
            MotionHandler().run(args['action'], args)
            count += 1
            os.unlink(p)
        except Exception:
            logger.error(
                'Error uploading orphaned file: %s', p, exc_info=True
            )
    if count > 0:
        logger.warning(
            'motion_handler.py cron run uploaded %d orphaned files', count
        )
    logger.info('Finished cron run')


def daemonize():
    pid = os.fork()
    try:
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        logging.error("Failed to Demonize: %d, %s\n" % (e.errno,e.strerror))
        sys.exit(1)
    os.setsid()
    pid = os.fork()
    try:
        if pid > 0:
            sys.exit(0)
    except OSError as e:
        logging.error("Failed to Demonize: %d, %s\n" % (e.errno,e.strerror))
        sys.exit(1)
    sys.stdout.flush()
    sys.stderr.flush()


def main(args):
    global logger, settings, motion_ingest, get_s3_bucket, boto3
    if args.config is not None:
        os.environ['MOTION_SETTINGS_PATH'] = args.config
    settings = importlib.import_module('motion_pipeline.settings')
    from motion_pipeline.s3connection import get_s3_bucket
    import boto3
    if args.action == 'dump-settings':
        s = settings.get_settings_dict()
        for k in sorted(s.keys()):
            print('%s = %s' % (k, s[k]))
        raise SystemExit(0)
    # This references 'settings', so must be imported after that module
    motion_ingest = importlib.import_module(
        'motion_pipeline.celerytasks.tasks'
    ).motion_ingest
    logging.basicConfig(**get_basicconfig_kwargs(args))
    logger = logging.getLogger()
    for lname in ['boto3', 'botocore', 's3transfer']:
        l = logging.getLogger(lname)
        l.setLevel(logging.WARNING)
        l.propagate = True
    if args.action == 'event_end' and args.text_event == '':
        logger.warning('Empty event_end; exiting')
        raise SystemExit(0)
    if args.action == 'cron':
        runcron()
        raise SystemExit(0)
    arg_dict = {
        'cam': args.cam_num,
        'changed_px': args.changed_px,
        'call_date': args.call_date,
        'event_id': args.event_id,
        'filename': args.filename,
        'filetype': args.filetype,
        'frame_num': args.frame_num,
        'motion_center_x': args.motion_center_x,
        'motion_center_y': args.motion_center_y,
        'motion_height': args.motion_height,
        'motion_width': args.motion_width,
        'noise': args.noise,
        'text_event': args.text_event,
        'action': args.action,
        'cam_name': args.cam_name,
        'threshold': args.threshold,
        'despeckle_labels': args.despeckle_labels,
        'fps': args.fps,
        'host': args.host
    }
    if arg_dict.get('text_event', None) is None:
        arg_dict['text_event'] = datetime.now().strftime('%Y%m%d%H%M%S')
        logger.debug('set text_event to: %s', arg_dict['text_event'])
    save_fname = arg_dict['filename']
    if save_fname is None:
        save_fname = '%s_%s' % (arg_dict['text_event'], args.action)
    try:
        MotionHandler().run(args.action, arg_dict)
    except Exception:
        p = os.path.join(
            settings.MOTION_SAVE_DIR, '%s.json' % save_fname
        )
        with open(p, 'w') as fh:
            fh.write(serialize(arg_dict))
        logger.critical(
            'Unhandled exception; JSON written to: %s', p, exc_info=True
        )
        raise
    logger.info('Completed %s in %.4fs', args.action, time.time() - START_TIME)


def entrypoint():
    p = psutil.Process()
    # nice -n 12 ionice -c 2 -n 6 nohup
    p.nice(12)
    p.ionice(psutil.IOPRIO_CLASS_BE, 6)
    args = parse_args(sys.argv[1:])
    if not args.foreground:
        daemonize()
    main(args)


if __name__ == "__main__":
    entrypoint()
