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

"""Tests for quantum state tomography."""

from qiskit_experiments.library import StateTomography
from qiskit import QuantumCircuit
from qiskit.quantum_info import DensityMatrix, state_fidelity

from qiskit_neko import decorators
from qiskit_neko.tests import base


class TestQuantumStateTomography(base.BaseTestCase):
    """Tests adapted from circuit basics tutorial."""

    @decorators.component_attr("terra", "backend", "experiment")
    def test_ghz_circuit_quantum_info(self):
        """Test state tomography of ghz state circuit"""
        nq = 3
        qc_ghz = QuantumCircuit(nq)
        qc_ghz.h(0)
        qc_ghz.s(0)
        for i in range(1, nq):
            qc_ghz.cx(0, i)
        qstexp1 = StateTomography(qc_ghz)
        qstdata1 = qstexp1.run(self.backend, seed_simulation=42).block_for_results()
        state_result = qstdata1.analysis_results("state")
        density_matrix = state_result.value
        ideal_density_matrix = DensityMatrix(qc_ghz)
        fidelity = state_fidelity(density_matrix, ideal_density_matrix)
        self.assertGreaterEqual(fidelity, 0.55)
