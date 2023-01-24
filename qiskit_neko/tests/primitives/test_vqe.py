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

"""Test primitives with vqe."""

from qiskit.algorithms.minimum_eigensolvers import VQE, SamplingVQE
from qiskit.algorithms.optimizers import SPSA
from qiskit.circuit.library import TwoLocal
from qiskit.opflow import PauliSumOp
from qiskit.primitives import BackendEstimator, BackendSampler
from qiskit.quantum_info import SparsePauliOp
from qiskit.utils import algorithm_globals
from qiskit_aer.primitives import Estimator, Sampler

from qiskit_neko import decorators
from qiskit_neko.tests import base


class TestVQEPrimitives(base.BaseTestCase):
    """Test the use of the execute() method in qiskit-terra."""

    def setUp(self):
        super().setUp()
        algorithm_globals.random_seed = 42
        if hasattr(self.backend.options, "seed_simulator"):
            self.backend.set_options(seed_simulator=42)

    @decorators.component_attr("terra", "backend")
    def test_sampling_vqe(self):
        """Test the execution of SamplingVQE with BackendSampler."""
        sampler = BackendSampler(self.backend)
        operator = PauliSumOp(SparsePauliOp(["ZZ", "IZ", "II"], coeffs=[1, -0.5, 0.12]))
        ansatz = TwoLocal(rotation_blocks=["ry", "rz"], entanglement_blocks="cz")
        optimizer = SPSA()
        sampling_vqe = SamplingVQE(sampler, ansatz, optimizer)
        result = sampling_vqe.compute_minimum_eigenvalue(operator)
        eigenvalue = result.eigenvalue
        expected = -1.38
        self.assertAlmostEqual(expected, eigenvalue, delta=0.3)

    @decorators.component_attr("terra", "aer")
    def test_aer_sampling_vqe(self):
        """Test the aer sampler with SamplingVQE."""
        sampler = Sampler(backend_options={"seed_simulator": 42})
        operator = PauliSumOp(SparsePauliOp(["ZZ", "IZ", "II"], coeffs=[1, -0.5, 0.12]))
        ansatz = TwoLocal(rotation_blocks=["ry", "rz"], entanglement_blocks="cz")
        optimizer = SPSA()
        sampling_vqe = SamplingVQE(sampler, ansatz, optimizer)
        result = sampling_vqe.compute_minimum_eigenvalue(operator)
        eigenvalue = result.eigenvalue
        expected = -1.38
        self.assertAlmostEqual(expected, eigenvalue, delta=0.3)

    @decorators.component_attr("terra", "backend")
    def test_vqe(self):
        """Test the execution of VQE with BackendEstimator."""
        estimator = BackendEstimator(self.backend)
        operator = PauliSumOp(SparsePauliOp(["ZZ", "IZ", "II"], coeffs=[1, -0.5, 0.12]))
        ansatz = TwoLocal(rotation_blocks=["ry", "rz"], entanglement_blocks="cz")
        optimizer = SPSA()
        sampling_vqe = VQE(estimator, ansatz, optimizer)
        result = sampling_vqe.compute_minimum_eigenvalue(operator)
        eigenvalue = result.eigenvalue
        expected = -1.38
        self.assertAlmostEqual(expected, eigenvalue, delta=0.3)

    @decorators.component_attr("terra", "aer")
    def test_aer_vqe(self):
        """Test the execution of VQE with Aer Estimator."""
        estimator = Estimator(backend_options={"seed_simulator": 42})
        operator = PauliSumOp(SparsePauliOp(["ZZ", "IZ", "II"], coeffs=[1, -0.5, 0.12]))
        ansatz = TwoLocal(rotation_blocks=["ry", "rz"], entanglement_blocks="cz")
        optimizer = SPSA()
        sampling_vqe = VQE(estimator, ansatz, optimizer)
        result = sampling_vqe.compute_minimum_eigenvalue(operator)
        eigenvalue = result.eigenvalue
        expected = -1.38
        self.assertAlmostEqual(expected, eigenvalue, delta=0.3)
