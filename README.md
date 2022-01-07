# qiskit-neko

[![License](https://img.shields.io/github/license/Qiskit/qiskit-neko.svg?style=popout-square)](https://opensource.org/licenses/Apache-2.0)

This repository contains integration tests for Qiskit. These tests are used
for primarily for two purposes as backwards compatibility testing for Qiskit
to validate that changes proposed to any Qiskit project do not break
functionality from previous release and to validate that functionality works
as expected with different providers. A provider in Qiskit is a package that
provides [backend](https://qiskit.org/documentation/stubs/qiskit.providers.BackendV2.html)
objects that provide an interface to Quantum hardware or a simulator.

## Installing qiskit-neko

Currently qiskit-neko is not designed to run as a standalone package and you
need to checkout the git source repository to run it. This is done to simplify
the execution of the tests as qiskit-neko leverages the
[``stestr``](https://github.com/mtreinish/stestr) for the execution of its
tests. To install qiskit-neko you need to first clone it with
[git](https://git-scm.com/):

```
git clone https://github.com/mtreinish/qiskit-neko.git
```

then you can install it using pip into your python environment

```
pip install .
```

Eventually a mode with a standalone package might be added, but for now this
is how you need to install qiskit-neko.

## Running tests

The simplest way to run the qiskit-neko test suite is to leverage
[``tox``](https://tox.wiki/en/latest/). The ``neko`` tox job is configured
to install qiskit-neko and then run the full test suite. After installing
``tox`` (typically done with ``pip install tox``) you can simply run:

```
tox -e neko
```

and this will install qiskit-neko into an isolated virtual environment and
then run tests.

If you don't wish to use tox to run tests. You can leverage ``stestr`` directly
to execute tests. Simply running:

```
stestr run
```

from the root of repository after installing qiskit-neko in your python
environment.

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

