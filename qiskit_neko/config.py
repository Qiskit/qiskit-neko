# This code is part of Qiskit.
#
# (C) Copyright IBM 2022.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Configuration file"""


import logging

import voluptuous as vol
import yaml


LOG = logging.getLogger(__name__)

schema = vol.Schema(
    {
        vol.Optional("test_timeout", default=-1): float,
        vol.Optional("backend_plugin", default="aer"): str,
        vol.Optional("backend_selection", default=""): str,
        vol.Optional("backend_script", default=""): str,
    }
)


class NekoConfig:
    """The configuration class for Qiskit Neko."""

    def __init__(self, filename=None):
        """Initialize a new configuration object.

        :param str filename: The absolute path to the configuration file to
            use for this configuration object
        """
        self.filename = filename
        self.config = None
        if self.filename:
            self.load_config()

    def load_config(self):
        with open(self.filename, "r") as fd:
            raw_config = yaml.safe_load(fd.read())
        self.config = schema(raw_config)
