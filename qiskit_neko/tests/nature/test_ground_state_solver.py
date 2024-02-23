# This code is part of Qiskit.
#
# (C) Copyright IBM 2022, 2024.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Test ground state solvers."""
import unittest

from qiskit_algorithms import NumPyMinimumEigensolver, VQE
from qiskit_algorithms.optimizers import SLSQP
from qiskit.primitives import Estimator

import qiskit_nature
from qiskit_nature.second_q.algorithms import GroundStateEigensolver
from qiskit_nature.second_q.circuit.library import HartreeFock, UCCSD
from qiskit_nature.second_q.drivers import PySCFDriver
from qiskit_nature.second_q.mappers import JordanWignerMapper

from qiskit_neko.tests import base
from qiskit_neko import decorators


class TestGroundStateSolvers(base.BaseTestCase):
    """Test the use of the execute() method in qiskit-terra."""

    @unittest.skipIf(
        tuple(map(int, qiskit_nature.__version__.split(".")[:2])) < (0, 7),
        "This test is incompatible with qiskit_nature versions below 0.7.0",
    )
    @decorators.component_attr("terra", "backend", "nature", "algorithms")
    def test_ground_state_solver(self):
        """Test the execution of a bell circuit with an explicit shot count."""
        driver = PySCFDriver(atom="H 0.0 0.0 0.0; H 0.0 0.0 0.735", basis="sto3g")
        es_problem = driver.run()
        qubit_mapper = JordanWignerMapper()
        estimator = Estimator()
        optimizer = SLSQP()
        ansatz = UCCSD(
            es_problem.num_spatial_orbitals,
            es_problem.num_particles,
            qubit_mapper,
            initial_state=HartreeFock(
                es_problem.num_spatial_orbitals,
                es_problem.num_particles,
                qubit_mapper,
            ),
        )
        vqe_solver = VQE(estimator, ansatz, optimizer)
        vqe_solver.initial_point = [0.0] * ansatz.num_parameters
        calc = GroundStateEigensolver(qubit_mapper, vqe_solver)
        result = calc.solve(es_problem)

        # Calculate expected result from numpy solver
        numpy_solver = NumPyMinimumEigensolver()
        np_calc = GroundStateEigensolver(qubit_mapper, numpy_solver)
        expected = np_calc.solve(es_problem)
        self.assertAlmostEqual(result.hartree_fock_energy, expected.hartree_fock_energy)
        self.assertEqual(len(result.total_energies), 1)
        self.assertAlmostEqual(result.total_energies[0], expected.total_energies[0], delta=0.02)
