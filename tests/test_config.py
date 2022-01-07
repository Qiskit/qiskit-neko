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

"""Test configuration files."""

import unittest

import voluptuous as vol

from qiskit_neko import config


class TestConfig(unittest.TestCase):
    def test_load_config_empty(self):
        mock_open = unittest.mock.mock_open(read_data="")
        with unittest.mock.patch("qiskit_neko.config.open", mock_open):
            with self.assertRaises(vol.MultipleInvalid):
                config_obj = config.NekoConfig("fake_path")

    def test_load_config_fully_populated(self):
        data = """---
test_timeout: 60.0
backend_plugin: ibmq
backend_selection: brooklyn
backend_script: /tmp/script.py
"""
        mock_open = unittest.mock.mock_open(read_data=data)
        with unittest.mock.patch("qiskit_neko.config.open", mock_open):
            config_obj = config.NekoConfig("fake_path")
        expected = {
            "test_timeout": 60.0,
            "backend_plugin": "ibmq",
            "backend_selection": "brooklyn",
            "backend_script": "/tmp/script.py",
        }
        self.assertEqual(expected, config_obj.config)

    def test_load_config_invalid_timeout_type(self):
        data = """---
test_timeout: 60 seconds
"""
        mock_open = unittest.mock.mock_open(read_data=data)
        with unittest.mock.patch("qiskit_neko.config.open", mock_open):
            with self.assertRaises(vol.MultipleInvalid):
                config.NekoConfig("fake_path")
