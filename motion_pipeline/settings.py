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

import os
import logging
import importlib
import importlib.util

logger = logging.getLogger(__name__)
_loaded_settings = {}


def _import_from_module(m):
    return importlib.import_module(m)


def _import_from_path(p):
    module_name = 'motion_pipeline.imported_settings'
    spec = importlib.util.spec_from_file_location(module_name, p)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_settings_dict():
    """returns the dict of loaded settings"""
    return {
        x: _loaded_settings[x] for x in sorted(_loaded_settings.keys())
        if x.isupper()
    }


if 'MOTION_SETTINGS_PATH' in os.environ:
    p = os.environ.get('MOTION_SETTINGS_PATH')
    if os.path.isabs(p):
        logger.debug('Attempting to import settings module from path: %s', p)
        m = _import_from_path(p)
    else:
        logger.debug('Attempting to import settings module from module: %s', p)
        m = _import_from_module(p)
    module_dict = m.__dict__
    try:
        to_import = m.__all__
    except AttributeError:
        to_import = [name for name in module_dict if not name.startswith('_')]
    v = {name: module_dict[name] for name in to_import}
    logger.debug('Import from MOTION_SETTINGS_PATH: %s', v)
    _loaded_settings = v
    globals().update(v)
else:
    raise RuntimeError('MOTION_SETTINGS_PATH not defined')
