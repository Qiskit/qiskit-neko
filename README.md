# qiskit-neko

[![License](https://img.shields.io/github/license/Qiskit/qiskit-neko.svg?style=popout-square)](https://opensource.org/licenses/Apache-2.0)

This repository contains integration tests for Qiskit. These tests are used
for primarily for two purposes as backwards compatibility testing for Qiskit
to validate that changes proposed to any Qiskit project do not break
functionality from previous release and to validate that functionality works
as expected with different providers. A provider in Qiskit is a package that
provides [backend](https://qiskit.org/documentation/stubs/qiskit.providers.BackendV2.html)
objects that provide an interface to Quantum hardware or a simulator.

## Qiskit Version compatibility

Due to its use for backwards compatibility testing there are strict requirements
on how we run CI for qiskit-neko. The qiskit-neko repository itself will only
run CI on released versions of upstream dependencies. This includes Qiskit
itself and other qiskit projects that are included in the tests here. A test can
not be added to qiskit-neko unless it will work with a released version of a
Qiskit component. All Qiskit components that contain tests in qiskit-neko must
run qiskit-neko in their CI (only the subset of tests which use that component)
using the proposed dev versions. A cron job running from either stable branches
or releases is recommend as well to ensure that nothing bit rots on code that
doesn't change as frequently.

If qiskit or any qiskit component starts supporting more than one release series
at a time. Additional CI jobs should be added to qiskit-neko to ensure we have
coverage of those multiple releases to ensure that functionality continues to
work across all supported releases.

This is done to ensure that backwards compatibility is maintained. Since
qiskit-neko is an external project to the rest of qiskit, to make a change to
the tests you must push a pull request to qiskit-neko and qiskit-neko will only
run CI from released version we validate the current functionality works. Then
since all projects tested by qiskit-neko are required to run qiskit-neko on
proposed changes we are checking that all the functionality we doesn't regress
with the proposed change applied..


## License

[Apache License 2.0](LICENSE.txt)

