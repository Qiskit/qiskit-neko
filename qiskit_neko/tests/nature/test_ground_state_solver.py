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

"""Test ground state solvers."""

import math

from qiskit.algorithms import NumPyMinimumEigensolver
from qiskit_nature.drivers import UnitsType, Molecule
from qiskit_nature.drivers.second_quantization import (
    ElectronicStructureDriverType,
    ElectronicStructureMoleculeDriver,
)
from qiskit_nature.problems.second_quantization import ElectronicStructureProblem
from qiskit_nature.converters.second_quantization import QubitConverter
from qiskit_nature.mappers.second_quantization import JordanWignerMapper
from qiskit.utils import QuantumInstance
from qiskit_nature.algorithms import VQEUCCFactory
from qiskit_nature.algorithms import GroundStateEigensolver

from qiskit_neko.tests import base
from qiskit_neko import decorators


class TestGroundStateSolvers(base.BaseTestCase):
    """Test the use of the execute() method in qiskit-terra."""

    def setUp(self):
        super().setUp()
        if hasattr(self.backend.options, "seed_simulator"):
            self.backend.set_options(seed_simulator=42)

    @decorators.component_attr("terra", "backend", "nature")
    def test_ground_state_solver(self):
        """Test the execution of a bell circuit with an explicit shot count."""
        molecule = Molecule(
            geometry=[["H", [0.0, 0.0, 0.0]], ["H", [0.0, 0.0, 0.735]]], charge=0, multiplicity=1
        )
        driver = ElectronicStructureMoleculeDriver(
            molecule, basis="sto3g", driver_type=ElectronicStructureDriverType.PYSCF
        )
        es_problem = ElectronicStructureProblem(driver)
        qubit_converter = QubitConverter(JordanWignerMapper())
        quantum_instance = QuantumInstance(self.backend)
        vqe_solver = VQEUCCFactory(quantum_instance)
        calc = GroundStateEigensolver(qubit_converter, vqe_solver)
        result = calc.solve(es_problem)
        # Calculate expected result from numpy solver
        numpy_solver = NumPyMinimumEigensolver()
        np_calc = GroundStateEigensolver(qubit_converter, numpy_solver)
        expected = np_calc.solve(es_problem)
        self.assertAlmostEqual(result.hartree_fock_energy, expected.hartree_fock_energy)
        self.assertEqual(len(result.total_energies), 1)
        self.assertAlmostEqual(result.total_energies[0], expected.total_energies[0], delta=0.02)
