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
from sqlalchemy import (
    Column, String, Integer, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship

try:
    from anyjson import serialize
    from anyjson import deserialize
except ImportError:
    from json import dumps as serialize
    from json import loads as deserialize

from motion_pipeline.database.models.base import Base, ModelAsDict

logger = logging.getLogger(__name__)


class Notification(Base, ModelAsDict):
    """
    Class that describes a database-persisted setting
    """

    __tablename__ = 'notifications'
    __table_args__ = (
        {'mysql_engine': 'InnoDB'}
    )

    #: Primary Key
    id = Column(Integer, primary_key=True)

    #: Name of the notification provider
    provider_name = Column(String(255))

    #: Video filename
    video_filename = Column(String(255), ForeignKey('videos.filename'))

    #: Video object relationship
    video = relationship('Video', uselist=False)

    #: The "text_event", a unique identifier for the event. This should be
    #: "%t-%Y%m%d%H%M%S-%q-%v"
    text_event = Column(String(255), ForeignKey('motion_events.text_event'))

    event = relationship('MotionEvent', uselist=False)

    #: datetime when the notification was generated
    generated_time = Column(DateTime)

    #: datetime when the notification was successfully sent
    sent_time = Column(DateTime)

    #: number of retries needed to send the notification
    num_retries = Column(Integer, default=0)

    #: the response from the provider
    provider_response = Column(String(255))
