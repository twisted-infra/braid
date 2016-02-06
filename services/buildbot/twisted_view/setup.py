#!/usr/bin/env python
#
# This file is part of Buildbot.  Buildbot is free software: you can
# redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright Buildbot Team Members

from setuptools import setup

setup(
    name='buildbot-twisted-view',
    description='Buildbot Console View plugin, hacked for Twisted',
    author=u'Pierre Tardy',
    author_email=u'tardyp@gmail.com',
    url='http://buildbot.net/',
    license='GNU GPL',
    packages=['buildbot_twisted_view'],
    package_data={
        '': [
            'VERSION',
            'static/img/*',
            'static/*.js',
            'static/*.css'
        ]
    },
    version='1',
    entry_points="""
        [buildbot.www]
        twisted_view = buildbot_twisted_view:ep
    """,
)
