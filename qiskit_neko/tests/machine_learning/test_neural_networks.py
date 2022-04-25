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

"""Tests for quantum neural networks."""

import numpy as np

from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.opflow import StateFn, PauliSumOp, ExpectationFactory, Gradient
from qiskit.utils import QuantumInstance

from qiskit_machine_learning.neural_networks import OpflowQNN

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
        """ Test the execution of quantum neural networks using OpflowQNN """

        expval = ExpectationFactory()
        gradient = Gradient()
        qi_sv = QuantumInstance(self.backend)

        params1 = [Parameter("input1"), Parameter("weight1")]
        qc1 = QuantumCircuit(1)
        qc1.h(0)
        qc1.ry(params1[0], 0)
        qc1.rx(params1[1], 0)
        qc_sfn1 = StateFn(qc1)

        h1 = StateFn(PauliSumOp.from_list([("Z", 1.0), ("X", 1.0)]))
        op1 = ~h1 @ qc_sfn1

        qnn1 = OpflowQNN(op1, [params1[0]], [params1[1]], expval, gradient, qi_sv)

        rng = np.random.default_rng(seed=42)
        input1 = rng.random(size = qnn1.num_inputs)
        weights1 = rng.random(size = qnn1.num_inputs)

        qnn1_forward = qnn1.forward(input1, weights1)
        qnn1_backward = qnn1.backward(input1, weights1)

        self.assertAlmostEqual(qnn1_forward[0][0], 0.08242345, delta = 0.0001)
        self.assertAlmostEqual(qnn1_backward[1][0][0], [0.2970094], delta = 0.0001)
