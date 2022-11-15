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
import sys

import numpy as np
from ddt import ddt, data
from qiskit.algorithms.optimizers import COBYLA
from qiskit.primitives import Sampler as ReferenceSampler
from qiskit.utils import algorithm_globals
from qiskit_aer.primitives import Sampler as AerSampler
from qiskit_machine_learning.algorithms.classifiers import VQC

from qiskit_neko import decorators
from qiskit_neko.tests import base


@ddt
class TestNeuralNetworkClassifierOnPrimitives(base.BaseTestCase):
    """Test adapted from the qiskit_machine_learning tutorials."""

    def setUp(self):
        super().setUp()
        if hasattr(self.backend.options, "seed_simulator"):
            self.backend.set_options(seed_simulator=42)

        self.samplers = dict(reference=ReferenceSampler(), aer=AerSampler())

    @decorators.component_attr("terra", "backend", "machine_learning")
    @data("reference", "aer")
    def test_neural_network_classifier(self, implementation):
        """Test the execution of quantum neural networks using OpflowQNN"""
        rng = np.random.default_rng(seed=42)
        algorithm_globals.random_seed = 42

        num_inputs = 2
        num_samples = 20
        x = 2 * rng.random(size=(num_samples, num_inputs)) - 1
        y01 = 1 * (np.sum(x, axis=1) >= 0)

        sampler = self.samplers[implementation]
        vqc = VQC(num_qubits=2, optimizer=COBYLA(maxiter=100), sampler=sampler)

        vqc.fit(x, y01)
        score = vqc.score(x, y01)
        print(score, file=sys.stderr)

        self.assertGreaterEqual(score, 0.5)