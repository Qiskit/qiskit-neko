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

"""Tests for quantum neural networks classifier."""

import numpy as np

from qiskit.circuit.library import RealAmplitudes, ZZFeatureMap
from qiskit.utils import QuantumInstance

from qiskit.algorithms.optimizers import COBYLA
from qiskit_machine_learning.algorithms.classifiers import VQC

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

        rng = np.random.default_rng(seed=42)

        num_inputs = 2
        num_samples = 20
        x = 2 * rng.random(size=(num_samples, num_inputs)) - 1
        y01 = 1 * (np.sum(x, axis=1) >= 0)
        y_one_hot = np.zeros((num_samples, 2))
        for i in range(num_samples):
            y_one_hot[i, y01[i]] = 1

        quantum_instance = QuantumInstance(self.backend)
        feature_map = ZZFeatureMap(num_inputs)
        ansatz = RealAmplitudes(num_inputs, reps=1)

        vqc = VQC(
            feature_map=feature_map,
            ansatz=ansatz,
            loss="cross_entropy",
            optimizer=COBYLA(),
            quantum_instance=quantum_instance,
        )

        vqc.fit(x, y_one_hot)
        score = vqc.score(x, y_one_hot)

        self.assertAlmostEqual(score, 0.7, delta=0.15)
