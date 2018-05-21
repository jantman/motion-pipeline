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

from setuptools import setup, find_packages
from motion_pipeline.version import VERSION, PROJECT_URL

with open('README.rst') as file:
    long_description = file.read()

# These should be just the absolute minimum requiremenrs for
# the motion_handler.py script to run.
requires = [
    'boto3>=1.7.0, <2.0.0',
    'psutil>=5.0.0, <6.0.0',
    'anyjson>=0.3.0, <1.0.0',
    'hiredis>=0.2.0, <1.0.0',
    'redis>=2.10.0, <3.0.0',
    'celery>=4.0.0, <5.0.0'
]

# Requirements for everything beyond that...
extras_require = {
    'web': [],
    'worker': [
        'PyMySQL>=0.8.0, <1.0.0',
        'SQLAlchemy-Utc>=0.10.0, <1.0.0',
        'SQLAlchemy>=1.2.0, <1.3.0'
    ]
}

all_req = list(set([
    req for item in extras_require for req in extras_require[item]
]))
extras_require['all'] = all_req

# @TODO - see: https://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'License :: OSI Approved :: GNU Affero General Public License '
    'v3 or later (AGPLv3+)',
    'Environment :: No Input/Output (Daemon)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Topic :: Home Automation',
    'Topic :: Multimedia :: Video',
    'Topic :: Other/Nonlisted Topic',
    'Topic :: Security',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3 :: Only'
]

setup(
    name='motion-pipeline',
    version=VERSION,
    author='Jason Antman',
    author_email='jason@jasonantman.com',
    packages=find_packages(),
    url=PROJECT_URL,
    description='Frontend and recording management pipeline for the Motion '
                'video motion detection project',
    long_description=long_description,
    install_requires=requires,
    extras_require=extras_require,
    entry_points={
        'console_scripts': [
            'motion-handler=motion_pipeline.motion_handler:entrypoint',
            'motion-queuepeek=motion_pipeline.celerytasks.queuepeek:main',
            'motion-initdb=motion_pipeline.database.initdb:main',
            'motion-dbshell=motion_pipeline.database.dbshell:main'
        ]
    },
    keywords="motion video frontend detection",
    classifiers=classifiers
)
