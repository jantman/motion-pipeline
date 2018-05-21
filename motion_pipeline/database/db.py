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
import os
import warnings
import motion_pipeline.settings as settings

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from pymysql.err import Warning


logger = logging.getLogger(__name__)

logger.debug('Creating DB engine with connection: %s',
             settings.DB_CONNSTRING)

echo = False
if os.environ.get('SQL_ECHO', '') == 'true':
    echo = True

# For some reason, with PyMySQL, even setting sql_mode to TRADITIONAL isn't
# raising an Exception when data is truncated. So we need to explicitly convert
# ``pymysql.err.Warning`` to an exception...
warnings.simplefilter('error', category=Warning)

engine_args = {
    'convert_unicode': True,
    'echo': echo,
    'pool_recycle': 3600
}

if settings.DB_CONNSTRING.startswith('mysql'):
    engine_args['connect_args'] = {'sql_mode': 'TRADITIONAL'}

if 'SQL_POOL_PRE_PING' in os.environ:
    engine_args['pool_pre_ping'] = True

#: The database engine object; return value of
#: :py:func:`sqlalchemy.create_engine`.
engine = create_engine(settings.DB_CONNSTRING, **engine_args)

logger.debug('Creating DB session')

#: :py:class:`sqlalchemy.orm.scoping.scoped_session` session
db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

logger.debug('Setting up Base and query')

from motion_pipeline.database.models.base import Base  # noqa
Base.query = db_session.query_property()


def init_db():
    """
    Initialize the database; call
    :py:meth:`sqlalchemy.schema.MetaData.create_all` on the metadata object.
    """
    logger.debug('Initializing database')
    Base.metadata.create_all(engine)
    logger.debug('Done initializing DB')


def cleanup_db():
    """
    This must be called from all scripts, using

        atexit.register(cleanup_db)

    """
    logger.debug('Closing DB session')
    db_session.remove()
