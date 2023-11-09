# This code is part of Qiskit.
#
# (C) Copyright IBM 2022, 2023.
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
from ddt import ddt, data, unpack
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.primitives import Sampler as ReferenceSampler, Estimator as ReferenceEstimator
from qiskit.quantum_info import SparsePauliOp

from qiskit_aer.primitives import Sampler as AerSampler, Estimator as AerEstimator
from qiskit_machine_learning.neural_networks import SamplerQNN, EstimatorQNN

from qiskit_neko import decorators
from qiskit_neko.tests import base


@ddt
class TestNeuralNetworksOnPrimitives(base.BaseTestCase):
    """Test adapted from the qiskit_machine_learning tutorials."""

    def setUp(self):
        super().setUp()

        self.input_params = [Parameter("x")]
        self.weight_params = [Parameter("w")]
        self.circuit = QuantumCircuit(1)
        self.circuit.ry(self.input_params[0], 0)
        self.circuit.rx(self.weight_params[0], 0)
        self.samplers = dict(reference=ReferenceSampler(), aer=AerSampler(run_options={"seed": 42}))
        self.estimators = dict(
            reference=ReferenceEstimator(), aer=AerEstimator(run_options={"seed": 42})
        )

    @decorators.component_attr("terra", "aer", "machine_learning")
    @data(["reference", 4], ["aer", 1])
    @unpack
    def test_sampler_qnn(self, implementation, decimal):
        """Test the execution of quantum neural networks using SamplerQNN."""
        sampler = self.samplers[implementation]

        qnn = SamplerQNN(
            circuit=self.circuit,
            input_params=self.input_params,
            weight_params=self.weight_params,
            input_gradients=True,
            sampler=sampler,
        )
        input_data = np.ones(len(self.input_params))
        weights = np.ones(len(self.weight_params))
        probabilities = qnn.forward(input_data, weights)
        np.testing.assert_array_almost_equal(probabilities, [[0.6460, 0.3540]], decimal)
        input_grad, weight_grad = qnn.backward(input_data, weights)
        np.testing.assert_array_almost_equal(input_grad, [[[-0.2273], [0.2273]]], decimal)
        np.testing.assert_array_almost_equal(weight_grad, [[[-0.2273], [0.2273]]], decimal)

    @decorators.component_attr("terra", "aer", "machine_learning")
    @data(["reference", 4], ["aer", 1])
    @unpack
    def test_estimator_qnn(self, implementation, decimal):
        """Test the execution of quantum neural networks using EstimatorQNN."""
        estimator = self.estimators[implementation]

        qnn = EstimatorQNN(
            circuit=self.circuit,
            observables=SparsePauliOp.from_list([("Z", 1)]),
            input_params=self.input_params,
            weight_params=self.weight_params,
            input_gradients=True,
            estimator=estimator,
        )
        input_data = np.ones(len(self.input_params))
        weights = np.ones(len(self.weight_params))
        expectations = qnn.forward(input_data, weights)
        np.testing.assert_array_almost_equal(expectations, [[0.2919]], decimal)
        input_grad, weight_grad = qnn.backward(input_data, weights)
        np.testing.assert_array_almost_equal(input_grad, [[[-0.4546]]], decimal)
        np.testing.assert_array_almost_equal(weight_grad, [[[-0.4546]]], decimal)
