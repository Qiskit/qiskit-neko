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

"""Tests for quantum neural networks Two Layer QNN."""

import numpy as np

from qiskit.circuit.library import RealAmplitudes, ZZFeatureMap
from qiskit.opflow import PauliSumOp
from qiskit.utils import QuantumInstance

from qiskit_machine_learning.neural_networks import TwoLayerQNN

from qiskit_neko.tests import base
from qiskit_neko import decorators


class TestNeuralNetworks(base.BaseTestCase):
    """Test adapted from the qiskit_machine_learning tutorials."""

    def setUp(self):
        super().setUp()
        if hasattr(self.backend.options, "seed_simulator"):
            self.backend.set_options(seed_simulator=42)

    @decorators.component_attr("terra", "backend", "machine_learning")
    def test_neural_networks(self):
        """Test the execution of quantum neural networks using OpflowQNN"""

        num_qubits = 3
        qi_sv = QuantumInstance(self.backend)

        fm = ZZFeatureMap(num_qubits, reps=2)
        ansatz = RealAmplitudes(num_qubits, reps=1)

        observable = PauliSumOp.from_list([("Z" * num_qubits, 1)])

        qnn3 = TwoLayerQNN(
            num_qubits, feature_map=fm, ansatz=ansatz, observable=observable, quantum_instance=qi_sv
        )

        rng = np.random.default_rng(seed=42)
        input3 = rng.random(size=qnn3.num_inputs)
        weights3 = rng.random(size=qnn3.num_weights)

        qnn3_forward = qnn3.forward(input3, weights3)
        qnn3_backward = qnn3.backward(input3, weights3)

        qnn3_backward_ideal = [
            0.0404151,
            0.20428904,
            -0.29863051,
            0.15322033,
            0.10620678,
            -0.2779404,
        ]

        self.assertAlmostEqual(qnn3_forward[0][0], -0.66604201, delta=0.1)
        qnn3_backward_result = qnn3_backward[1][0][0].tolist()
        for count, ele in enumerate(qnn3_backward_ideal):
            self.assertAlmostEqual(qnn3_backward_result[count], ele, delta=0.1)
