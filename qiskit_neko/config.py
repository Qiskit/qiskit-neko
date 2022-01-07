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

LOG_LEVEL_VALIDATOR = vol.Any("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


schema = vol.Schema(
    {
        vol.Optional("test_timeout"): vol.Coerce(float),
        vol.Optional("backend_plugin", default="aer"): str,
        vol.Optional("backend_selection"): str,
        vol.Optional("backend_script"): str,
        vol.Optional("default_log_level", default="INFO"): LOG_LEVEL_VALIDATOR,
        vol.Optional("module_log_level"): {vol.Extra: LOG_LEVEL_VALIDATOR},
        vol.Optional("log_format"): str,
        vol.Optional("log_file"): str,
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
