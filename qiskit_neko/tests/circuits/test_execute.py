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

"""Test backend on execute()."""

import math

from qiskit.circuit import QuantumCircuit
from qiskit import transpile

from qiskit_neko import decorators
from qiskit_neko.tests import base


class TestExecute(base.BaseTestCase):
    """Test the use of the execute() method in qiskit-terra."""

    def setUp(self):
        super().setUp()
        if not hasattr(self.backend.options, "shots"):
            raise self.skipException(
                "Provided backend {self.backend} does not have a configurable shots option"
            )
        if hasattr(self.backend.options, "seed_simulator"):
            self.backend.set_options(seed_simulator=42)

    @decorators.component_attr("terra", "backend")
    def test_bell_execute_fixed_shots(self):
        """Test the execution of a bell circuit with an explicit shot count."""
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure_all()
        job = self.backend.run(transpile(circuit, self.backend), shots=100)
        result = job.result()
        counts = result.get_counts()
        self.assertDictAlmostEqual(counts, {"00": 50, "11": 50}, delta=10)

    @decorators.component_attr("terra", "backend")
    def test_bell_execute_default_shots(self):
        """Test the execution of a bell circuit with an explicit shot count."""
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure_all()
        expected_count = self.backend.options.shots / 2
        job = self.backend.run(transpile(circuit, self.backend))
        result = job.result()
        counts = result.get_counts()
        delta = 10 ** (math.log10(self.backend.options.shots) - 1)
        self.assertDictAlmostEqual(
            counts, {"00": expected_count, "11": expected_count}, delta=delta
        )

    @decorators.component_attr("terra", "backend")
    def test_bell_execute_backend_shots_set_options(self):
        """Test the execution of a bell circuit with an explicit shot count set via options."""
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure_all()
        self.backend.set_options(shots=100)
        job = self.backend.run(transpile(circuit, self.backend))
        result = job.result()
        counts = result.get_counts()
        self.assertDictAlmostEqual(counts, {"00": 50, "11": 50}, delta=10)
