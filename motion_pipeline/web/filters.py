"""
The latest version of this package is available at:
<http://github.com/jantman/motion-pipeline>

##################################################################################
Copyright 2017 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

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

from jinja2.runtime import Undefined
from humanize import naturaltime

from motion_pipeline.utils import dtnow
from motion_pipeline.web.app import app
from motion_pipeline.database.models import EventDispositionEnum


@app.template_filter('ago')
def ago_filter(dt):
    """
    Format a datetime using humanize.naturaltime, "ago"

    :param dt: datetime to compare to now
    :type dt: datetime.datetime
    :return: ago string
    :rtype: str
    """
    if dt == '' or dt is None or isinstance(dt, Undefined):
        return ''
    return naturaltime(dtnow() - dt)


@app.template_filter('motionpercent')
def motionpercent_filter(image_w, image_h, motion_w, motion_h):
    """
    Given the dimensions of the full image and of the motion area, return the
    percentage of the full image that the motion area makes up.

    :param image_w: full image width
    :type image_w: int
    :param image_h: full image height
    :type image_h: int
    :param motion_w: motion area width
    :type motion_w: int
    :param motion_h: motion area height
    :type motion_h: int
    :return: percentage of image that motion area makes up
    :rtype: float
    """
    img = image_w * image_h
    motion = motion_w * motion_h
    return (motion / img) * 100


@app.template_filter('dispositionlinks')
def dispositionlinks_filter(event):
    s = ''
    dispos = {k: k.name for k in EventDispositionEnum}
    dispos[None] = 'none'
    for k in dispos:
        if event.disposition == k:
            s += '<strong>%s</strong> ' % dispos[k]
        else:
            s += '<a href="#" onclick="setDisposition(text_event, \'%s\')">%s</a> ' % (
                dispos[k], dispos[k]
            )
    return s
