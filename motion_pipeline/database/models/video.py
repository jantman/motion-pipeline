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
    Column, Integer, String, DateTime, Boolean, ForeignKey, Numeric
)
from sqlalchemy.orm import relationship
from motion_pipeline.database.models.base import Base, ModelAsDict

logger = logging.getLogger(__name__)


class Video(Base, ModelAsDict):
    """
    Class that describes a video file upload from motion
    """

    __tablename__ = 'videos'
    __table_args__ = (
        {'mysql_engine': 'InnoDB'}
    )

    #: Primary Key
    filename = Column(String(255), primary_key=True)

    #: Name of thumbnail file
    thumbnail_name = Column(String(255))

    #: date of the upload
    date = Column(DateTime)

    #: datetime when motion called motion_handler.py for on_movie_end
    handler_call_datetime = Column(DateTime)

    #: ID of the event; this resets every time motion restarts
    event_id = Column(Integer)

    #: The camera number
    cam_num = Column(Integer)

    #: The camera name
    cam_name = Column(String(40))

    #: The host that motion is running on
    host = Column(String(40))

    #: The "text_event", a unique identifier for the event. This should be
    #: "%t-%Y%m%d%H%M%S-%q-%v"
    text_event = Column(String(255), ForeignKey('motion_events.text_event'))

    event = relationship('MotionEvent', back_populates='video', uselist=False)

    #: The file type
    file_type = Column(Integer)

    #: The current threshold setting for motion detection
    threshold = Column(Integer)

    #: The number of labels identified by despeckle
    despeckle_labels = Column(Integer)

    #: The current FPS rate of the camera
    fps = Column(Integer)

    #: The length of the video in seconds
    length_sec = Column(Numeric)

    #: Whether or not the file has been viewed yet
    is_viewed = Column(Boolean, default=False)

    #: Whether or not the file is flagged to archive
    is_archived = Column(Boolean, default=False)
