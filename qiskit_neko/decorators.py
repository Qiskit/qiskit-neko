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

# pylint: disable=missing-param-doc

"""qiskit-neko decorators."""

import testtools


def component_attr(*args, condition=None):
    """A decorator which applies the testtools attr decorator

    This decorator applies the testtools.testcase.attr if it is in the list of
    attributes to testtools we want to apply.

    :param *args: The component names to apply as attributes to the tests. This
        is typically the project name or feature being tested by the test
        method, for example ``"terra", ``"backend"``, ``"nature"``, etc.
        It provides users a common filter string to easily run a subset of
        tests that use a particular component or feature.
    :param bool condition: Optional condition which if true will apply the
        attr. If a condition is specified which is false the attr will not be
        applied to the test function. If not specified, the attr is always
        applied.
    """

    def decorator(func):
        # Check to see if the attr should be conditional applied.
        if condition is not None and not condition:
            return func
        for attr in args:
            func = testtools.testcase.attr(attr)(func)
        return func

    return decorator
