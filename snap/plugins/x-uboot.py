# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2016-2017 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""The u-boot plugin refines the generic kbuild plugin to allow building
u-boot inside gadget snaps from source in one shot...
"""

import logging
import os

import snapcraft
from snapcraft.plugins import kbuild

logger = logging.getLogger(__name__)

class UbootPlugin(kbuild.KBuildPlugin):

    @classmethod
    def schema(cls):
        schema = super().schema()

        schema['properties']['target-arch'] = {
            'oneOf': [
                {'type': 'string'},
                {'type': 'object'},
            ],
            'default': '',
        }
        return schema

    @classmethod
    def get_build_properties(cls):
        # Inform Snapcraft of the properties associated with building. If these
        # change in the YAML Snapcraft will consider the build step dirty.
        return super().get_build_properties() + ['target-arch']

    def __init__(self, name, options, project):
        super().__init__(name, options, project)

        if self.options.target_arch:
            logger.info('Overriding ARCH definition with {!r}'.format(self.options.target_arch))
            if isinstance(self.options.target_arch, str):
                self.make_cmd.append('ARCH={}'.format(self.options.target_arch))
            elif self.project.deb_arch in self.options.target_arch:
                self.make_cmd.append('ARCH={}'.format(self.options.target_arch[self.project.deb_arch]))

    def enable_cross_compilation(self):
        logger.info('Cross compiling u-boot target {!r}'.format(
            self.project.kernel_arch))
        if not any("ARCH=" in s for s in self.make_cmd):
            self.make_cmd.append('ARCH={}'.format(
                self.project.kernel_arch))
        if 'CROSS_COMPILE' in os.environ:
            toolchain = os.environ['CROSS_COMPILE']
        else:
            toolchain = self.project.cross_compiler_prefix
        self.make_cmd.append('CROSS_COMPILE={}'.format(toolchain))

    def do_install(self):
        logger.info('Skipping install step for u-boot')
