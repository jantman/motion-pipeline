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
from functools import wraps

import redis

logger = logging.getLogger(__name__)


class SimpleCache(object):

    def __init__(self, broker_url, key_prefix):
        self._broker_url = broker_url
        self._key_prefix = key_prefix
        parsed = urlparse(self._broker_url)
        assert parsed.scheme == 'redis'
        logger.debug('Connecting to Redis at: %s', self._broker_url)
        self._redis = redis.StrictRedis(
            host=parsed.hostname, port=parsed.port, db=parsed.path.lstrip('/'),
            decode_responses=True
        )
        logger.debug('Connected to Redis.')

    def hash_set(self, key, value, ttl=60):
        path = self._key_prefix + key
        logger.debug('Setting cache hash "%s" to: %s', path, value)
        self._redis.hmset(path, value)
        logger.debug('Setting cache TTL on %s to: %d', path, ttl)
        self._redis.expire(path, ttl)

    def hash_get(self, key):
        """returns an empty dict if not in cache"""
        path = self._key_prefix + key
        return self._redis.hgetall(path)

    def string_set(self, key, value, ttl=60):
        path = self._key_prefix + key
        logger.debug(
            'Setting cache string "%s" to "%s" with TTL %d', path, value, ttl
        )
        self._redis.set(path, value, ex=ttl)

    def string_get(self, key):
        """returns None if not in cache"""
        path = self._key_prefix + key
        return self._redis.get(path)
