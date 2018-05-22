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
    Column, Integer, String, DateTime, Boolean
)
from sqlalchemy.orm import relationship
from motion_pipeline.database.models.base import Base, ModelAsDict

logger = logging.getLogger(__name__)


class MotionEvent(Base, ModelAsDict):
    """
    Class that describes a motion detected event
    """

    __tablename__ = 'motion_events'
    __table_args__ = (
        {'mysql_engine': 'InnoDB'}
    )

    #: The "text_event", a unique identifier for the event. This should be
    #: "%t-%Y%m%d%H%M%S-%q-%v"
    text_event = Column(String(255), primary_key=True)

    #: date of the upload
    date = Column(DateTime)

    #: ID of the event; this resets every time motion restarts
    event_id = Column(Integer)

    #: The frame number
    frame_num = Column(Integer)

    #: The camera number
    cam_num = Column(Integer)

    #: The camera name
    cam_name = Column(String(40))

    #: The host that motion is running on
    host = Column(String(40))

    #: The number of changed pixels
    changed_pixels = Column(Integer)

    #: The current threshold setting for motion detection
    threshold = Column(Integer)

    #: The noise level
    noise = Column(Integer)

    #: The number of labels identified by despeckle
    despeckle_labels = Column(Integer)

    #: The current FPS rate of the camera
    fps = Column(Integer)

    #: The width of the motion area in pixels
    motion_width = Column(Integer)

    #: The height of the motion area in pixels
    motion_height = Column(Integer)

    #: The X center of the motion area
    motion_center_x = Column(Integer)

    #: The Y center of the motion area
    motion_center_y = Column(Integer)

    upload = relationship('Upload', back_populates='event', uselist=False)

    #: Whether or not the file has been viewed yet
    is_finished = Column(Boolean, default=False)
