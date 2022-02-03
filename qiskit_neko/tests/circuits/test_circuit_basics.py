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

"""Tests from circuit basics tutorial."""

import math

import ddt
from qiskit import QuantumCircuit, transpile

from qiskit_neko import decorators
from qiskit_neko.tests import base


@ddt.ddt
class TestCircuitBasics(base.BaseTestCase):
    """Tests adapted from circuit basics tutorial."""

    def setUp(self):
        super().setUp()
        self.circ = QuantumCircuit(3)
        self.circ.h(0)
        self.circ.cx(0, 1)
        self.circ.cx(0, 2)

    @decorators.component_attr("terra", "backend")
    @ddt.data(0, 1, 2, 3)
    def test_ghz_circuit(self, opt_level):
        """Test execution of ghz circuit."""
        self.circ.measure_all()
        tqc = transpile(self.circ, self.backend, optimization_level=opt_level)
        run_kwargs = {}
        expected_value = None
        if hasattr(self.backend.options, "shots"):
            run_kwargs["shots"] = 1000
            expected_value = 500
        if hasattr(self.backend.options, "seed_simulator"):
            run_kwargs["seed_simulator"] = 42
        job = self.backend.run(tqc, **run_kwargs)
        result = job.result()
        counts = result.get_counts()
        if expected_value is None:
            expected_value = sum(counts.values()) / 2
        expected = {"000": expected_value, "111": expected_value}
        delta = 10 ** math.floor(math.log10(expected_value))
        self.assertDictAlmostEqual(counts, expected, delta=delta)
