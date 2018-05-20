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
from urllib.parse import urlparse
import redis
import json

import motion_pipeline.settings as settings

logger = logging.getLogger(__name__)

DEFAULT_QUEUE_NAME = 'celery'


class QueuePeek(object):

    def __init__(self):
        self._broker_url = settings.REDIS_BROKER_URL
        parsed = urlparse(self._broker_url)
        assert parsed.scheme == 'redis'
        logger.debug('Connecting to Redis at: %s', self._broker_url)
        self._redis = redis.StrictRedis(
            host=parsed.hostname, port=parsed.port, db=parsed.path.lstrip('/')
        )
        logger.debug('Connected to Redis.')

    def peek(self, queue_name):
        logger.debug('Checking length and contents of queue: %s', queue_name)
        queue_len = self._redis.llen(queue_name)
        logger.debug('Queue "%s" length: %d', queue_name, queue_len)
        if queue_len == 0:
            return []
        items = []
        for i in self._redis.lrange(queue_name, 0, -1):
            try:
                tmp = json.loads(i)
                items.append(tmp)
            except Exception:
                items.append(i)
        return items

    def printer(self, queue_name):
        content = self.peek(queue_name)
        print(json.dumps(content, sort_keys=True, indent=4))


def main():
    QueuePeek().printer(DEFAULT_QUEUE_NAME)
