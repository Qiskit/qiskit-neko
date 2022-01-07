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

from qiskit.circuit import QuantumCircuit
from qiskit import execute

from qiskit_neko.tests import base


class TestExecute(base.BaseTestCase):
    def test_bell_execute(self):
        circuit = QuantumCircuit(2)
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure_all()
        job = execute(circuit, self.backend, shots=1000)
        result = job.result()
        counts = result.get_counts()
        self.assertDictAlmostEqual(counts, {"00": 500, "11": 500}, delta=100)
