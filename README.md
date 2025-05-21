# qiskit-neko

[![License](https://img.shields.io/github/license/Qiskit/qiskit-neko.svg?style=popout-square)](https://opensource.org/licenses/Apache-2.0)

  - You can see the full rendered docs at:
    https://qiskit.github.io/qiskit-neko/


This repository contains integration tests for Qiskit. These tests are used
primarily for two purposes: as backwards compatibility testing for Qiskit
to validate that changes proposed to any Qiskit project do not break
functionality from previous release and to validate that functionality works
as expected with different providers. A provider in Qiskit is a package that
provides [backend](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.providers.BackendV2)
objects that provide an interface to Quantum hardware or a simulator.

## Installing qiskit-neko

Currently qiskit-neko is not designed to run as a standalone package and you
need to checkout the git source repository to run it. This is done to simplify
the execution of the tests as qiskit-neko leverages 
[``stestr``](https://github.com/Qiskit/stestr) for the execution of its
tests. To install qiskit-neko you need to first clone it with
[git](https://git-scm.com/):

```
git clone https://github.com/Qiskit/qiskit-neko.git
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
to execute tests. Simply run:

```
stestr run
```

from the root of the repository after installing qiskit-neko in your python
environment.

## Qiskit Version compatibility

Due to its use for backwards compatibility testing there are strict requirements
on how we run CI for qiskit-neko. The qiskit-neko repository itself will only
run CI on released versions of upstream dependencies. This includes Qiskit
itself and other Qiskit projects that are included in the tests here. A test can
not be added to qiskit-neko unless it will work with a released version of a
Qiskit component. All Qiskit components that contain tests in qiskit-neko must
run qiskit-neko in their CI (only the subset of tests which use that component)
using the proposed dev versions. A cron job running from either stable branches
or releases is recommend as well to ensure that nothing bit rots on code that
doesn't change as frequently.

If Qiskit or any Qiskit component starts supporting more than one release series
at a time, additional CI jobs should be added to qiskit-neko to ensure we have
coverage of those multiple releases to ensure that functionality continues to
work across all supported releases.

This is done to ensure that backwards compatibility is maintained. Since
qiskit-neko is an external project to the rest of Qiskit, to make a change to
the tests you must push a pull request to qiskit-neko and qiskit-neko will only
run CI from released version we validate the current functionality works. Then
since all projects tested by qiskit-neko are required to run qiskit-neko on
proposed changes we are checking that all the functionality we add doesn't regress
with the proposed change applied.

### Downstream usage in testing

The expectation is for any Qiskit project that includes tests in qiskit-neko that
they run in CI against their ``main`` branch with a pre-merge CI job, while all
other Qiskit components are using **released** versions published on pypi. This is
for two reasons primarily. First it is done to ensure we're actually testing
what users actually run and that any potential compatibility issues between
released versions and a potential change are caught prior to a release. The
API stability guarantees provided by Qiskit projects only apply at release and
for an integration test suite we only are concerned that we do not break
compatibility with what users will be running and that there is an upgrade path
for each project. Secondly, this is necessary because of limitations in the
publicly available CI systems on github. We do not have mechanisms in CI to
enable co-gating or testing a PR with more than one proposed change applied (to
1 or more repository) so if we were to enable bidirectional CI (where an
upstream project is run from main at the same time as the project under test
and vice versa) there is a high probability of having the job broken on both sides
without a way to unblock it without merging a PR that does not have passing CI.

### Intentional API changes

As many Qiskit projects don't strictly adhere to the use of public APIs exposed
by the upstream Qiskit projects there are situations that come up where an
intentional API change to fix a bug or other scenario results in a break of
a downstream project. In such situations a careful procedure needs to be
followed to acknowledge the change and ensure it's clearly documented both
in the upstream project's release documentation as well as for the downstream
projects effected. The following procedure should be used to ensure this
happens:

1. Propose a PR to the upstream project that is failing qiskit-neko CI and
   has the appropriate release note. This will need an acknowledgement by a
   core team member that it is an acceptable change.
2. Propose a PR to the downstream projects effected by the change proposed in
   #1 that makes the necessary updates to account for #1. This PR will likely
   also fail the qiskit-neko job which is expected until #1 is included in a
   new release of the upstream project.
3. Propose a PR and tracking issue to qiskit-neko that adds a skip on the test
   with a skip message that refers to the tracking issue. This skip will remain
   in place until #1 and #2 are included in a release.
   - If a test change is necessary propose that change along with the skip.
4. When #1 and #2 are both released with the fix propose a PR removing the skip
   from qiskit-neko that closes the tracking issue.


## License

[Apache License 2.0](LICENSE.txt)

