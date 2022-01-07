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

# pylint: disable=invalid-name

"""Backend plugin interface."""


import abc
import logging

import stevedore

LOG = logging.getLogger(__name__)


class BackendPlugin(abc.ABC):
    """Abstract class for providing :class:`~qiskit.providers.Backend` objects to tests

    This class is designed to be implemented by qiskit providers packages or any
    other user that needs to provide custom backend objects to the test suite.
    In general the authentication and initialization of working with backends
    from different vendors or with different simulators are all unique
    qiskit-neko provides the backend plugin interface to enable a standard
    interface to return backend objects and leave the specifics of
    authentication or initialization of providers.
    """

    @abc.abstractmethod
    def get_backend(self, backend_selection=None):
        """Return the Backend object to run tests on.

        :param str backend_selection: An optional user supplied value to select
            a specific backend. The exact behavior of this option is up to
            each individual plugin and should be clearly documented in the
            plugin how this is used if at all. If the plugin doesn't support
            a selection string a string should still be accepted and a warning
            just logged. If a string is provided (and they're accepted) but
            the string is invalid raising an exception is expected.
        """
        pass


class BackendPluginManager:
    """Class to manage installed backend plugins"""

    def __init__(self):
        self.ext_plugins = stevedore.ExtensionManager(
            "qiskit_neko.backend_plugins",
            invoke_on_load=True,
            propagate_map_exceptions=True,
            on_load_failure_callback=self.failure_hook,
        )

    @staticmethod
    def failure_hook(_, ep, err):
        """Hook method to execute on import failure."""
        LOG.error("Could not load %r: %s", ep.name, err)
        raise err

    def get_plugin_backends(self, backend_selection=None):
        """Return a dictionary of plugin names to backend objects."""
        return {
            plug.name: plug.obj.get_backend(backend_selection=backend_selection)
            for plug in self.ext_plugins
        }
