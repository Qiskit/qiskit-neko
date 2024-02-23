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

"""Qiskit Aer default backend plugin."""

import qiskit_aer as aer
from qiskit_ibm_runtime import fake_provider

from qiskit_neko import backend_plugin


class AerBackendPlugin(backend_plugin.BackendPlugin):
    """A backend plugin for using qiskit-aer as the backend."""

    def __init__(self):
        super().__init__()
        self.mock_provider = fake_provider.FakeProvider()
        self.mock_provider_backend_names = set()
        for backend in self.mock_provider.backends():
            if backend.version == 1:
                self.mock_provider_backend_names.add(backend.name())
            elif backend.version == 2:
                self.mock_provider_backend_names.add(backend.name)

    def get_backend(self, backend_selection=None):
        """Return the Backend object to run tests on.

        :param str backend_selection: An optional selection string to specify
            the backend object returned from this method. This can be used
            in two different ways. Either it can be used to specify a fake
            backend name from ``qiskit.test.mock`` in ``qiskit-terra`` such
            as ``fake_quito`` which will return that fake backend object or
            alternatively if the string starts with ``method=`` an ideal
            :class:`~qiskit.providers.aer.AerSimulator` object with that method
            will be set. If this is not specified a
            :class:`~qiskit.providers.aer.AerSimulator` will be returned with
            the defailt settings.
        :raises ValueError: If an invalid backend selection string is passed in
        """
        if backend_selection is None:
            return aer.AerSimulator()
        if backend_selection.startswith("method="):
            method = backend_selection.split("=")[1]
            return aer.AerSimulator(method=method)
        if backend_selection in self.mock_provider_backend_names:
            return self.mock_provider.get_backend(backend_selection)
        raise ValueError(f"Invalid selection string {backend_selection}.")
