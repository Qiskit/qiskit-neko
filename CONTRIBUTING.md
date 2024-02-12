# Contributing

First read the overall project contributing guidelines. These are all
included in the qiskit documentation:

https://github.com/Qiskit/qiskit/blob/main/CONTRIBUTING.md

## Contributing to qiskit-neko

In addition to the general guidelines there are specific details for
contributing to qiskit experiments, these are documented below.

## Qiskit Neko Test Guideline

Qiskit Neko is about integration testing, that is testing the combined Qiskit
deliverable. The purpose of these tests are to verify that the end user
Qiskit workflow is functional and stable moving forward. When adding tests
to Qiskit Neko it is useful to write the tests as if you were a Qiskit user
(not involved in upstream development at all) and evaluate the test like a
typical user would evaluate the API functionality. Tests should not ever access
private methods or internal attributes from qiskit projects.

The tests contained in Qiskit Neko ideally should involve > 1 Qiskit component
so that we're validating the integration of the wider qiskit ecosystem. Tests
that are isolated to a single Qiskit component are better tested in the the
local tests for that project.

### Writing Tests

Qiskit Neko tests are expected to be written using the stdlib unittest
style (although features from the extension package testtools are acceptable)
and will be executed by the stestr test runner. While locally you can use any
unittest compatible runner you wish for CI purposes stestr is used to enable
seamless parallel test execution.

Qiskit Neko tests are expected to work when run in parallel processes. All test
methods in the test suite should be compatible with running at the same time as
any other test method in the test suite. This means that if there are shared
global resources (such as files) needed for your test to function you should
ensure these resources are isolated from other tests. Additionally there is no
guarantees on test execution order in qiskit-neko, so no test should be added
to qiskit-neko that has an order dependency on any other test.

#### Test guidelines

When writing tests for Qiskit Neko there are some guidelines to keep in mind.

1. Tests should typically involve more than one Qiskit component
    (running a circuit on a configured backend is a second component)
2. Tests should typically try to return in <= 120 seconds if possible (when
    running in CI with qiskit-aer running with other providers can take longer).
    This is important to ensure we have a reasonable CI experience around running
    neko.
3. Tests should never assume being run with a particular backend. Qiskit Neko
    is used to validate provider implementations in addition to it's use
    as an integration/backwards compatibility test suite. All tests written in
    qiskit-neko
4. Negative tests (tests that generate a failure mode) are valid in Qiskit Neko
    assuming the failure mode is part of the published stable API being tested

#### Using backends

All test classes in qiskit-neko should be inherited from the base test class:
`BaseTestCase` (defined in:
https://github.com/Qiskit/qiskit-neko/blob/main/qiskit_neko/tests/base.py).
This base test class provides common setup functionality that automate most
of the necessary fixtures like setting per test timeouts and capturing stdout,
stderr, logging, etc.  But, for the purposes of using backends the base test
class also is where the plugin and config integration takes place. So if you
base your test class off of `BaseTestCase` the `setUp()` method will initialize
a `Backend` object for you (based on configuration and plugins) which is
accesible via `self.backend` in test methods. This should be used whenever
a backend is needed in a test method.
