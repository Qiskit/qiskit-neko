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

import inspect
import importlib.util
import logging
import os

import testtools
import fixtures

from qiskit_neko import backend_plugin
from qiskit_neko import config

LOG = logging.getLogger(__name__)


def dicts_almost_equal(dict1, dict2, delta=None, places=None, default_value=0):
    """Test if two dictionaries with numeric values are almost equal.
    Fail if the two dictionaries are unequal as determined by
    comparing that the difference between values with the same key are
    not greater than delta (default 1e-8), or that difference rounded
    to the given number of decimal places is not zero. If a key in one
    dictionary is not in the other the default_value keyword argument
    will be used for the missing value (default 0). If the two objects
    compare equal then they will automatically compare almost equal.
    Args:
        dict1 (dict): a dictionary.
        dict2 (dict): a dictionary.
        delta (number): threshold for comparison (defaults to 1e-8).
        places (int): number of decimal places for comparison.
        default_value (number): default value for missing keys.
    Raises:
        TypeError: if the arguments are not valid (both `delta` and
            `places` are specified).
    Returns:
        String: Empty string if dictionaries are almost equal. A description
            of their difference if they are deemed not almost equal.
    """

    def valid_comparison(value):
        """compare value to delta, within places accuracy"""
        if places is not None:
            return round(value, places) == 0
        else:
            return value < delta

    # Check arguments.
    if dict1 == dict2:
        return ""
    if places is not None:
        if delta is not None:
            raise TypeError("specify delta or places not both")
        msg_suffix = " within %s places" % places
    else:
        delta = delta or 1e-8
        msg_suffix = " within %s delta" % delta

    # Compare all keys in both dicts, populating error_msg.
    error_msg = ""
    for key in set(dict1.keys()) | set(dict2.keys()):
        val1 = dict1.get(key, default_value)
        val2 = dict2.get(key, default_value)
        if not valid_comparison(abs(val1 - val2)):
            error_msg += f"({key}: {val1} != {val2}), "

    if error_msg:
        return error_msg[:-2] + msg_suffix
    else:
        return ""


class _WrappedMethodCall:
    """Method call with extra functionality before and after.  This is returned by
    :obj:`~_WrappedMethod` when accessed as an atrribute."""

    def __init__(self, descriptor, obj, objtype):
        self.descriptor = descriptor
        self.obj = obj
        self.objtype = objtype

    def __call__(self, *args, **kwargs):
        if self.descriptor.isclassmethod:
            ref = self.objtype
        else:
            # obj if we're being accessed as an instance method, or objtype if as a class method.
            ref = self.obj if self.obj is not None else self.objtype
        for before in self.descriptor.before:
            before(ref, *args, **kwargs)
        out = self.descriptor.method(ref, *args, **kwargs)
        for after in self.descriptor.after:
            after(ref, *args, **kwargs)
        return out


class _WrappedMethod:
    """Descriptor which calls its two arguments in succession, correctly handling instance- and
    class-method calls.

    It is intended that this class will replace the attribute that ``inner`` previously was on a
    class or instance.  When accessed as that attribute, this descriptor will behave it is the same
    function call, but with the ``function`` called after.
    """

    def __init__(self, cls, name, before=None, after=None):
        # Find the actual definition of the method, not just the descriptor output from getattr.
        for cls_ in inspect.getmro(cls):
            try:
                self.method = cls_.__dict__[name]
                break
            except KeyError:
                pass
        else:
            raise ValueError(f"Method '{name}' is not defined for class '{cls.__class__.__name__}'")
        before = (before,) if before is not None else ()
        after = (after,) if after is not None else ()
        if isinstance(self.method, type(self)):
            self.isclassmethod = self.method.isclassmethod
            self.before = before + self.method.before
            self.after = self.method.after + after
            self.method = self.method.method
        else:
            self.isclassmethod = False
            self.before = before
            self.after = after
        if isinstance(self.method, classmethod):
            self.method = self.method.__func__
            self.isclassmethod = True

    def __get__(self, obj, objtype=None):
        # No functools.wraps because we're probably about to be bound to a different context.
        return _WrappedMethodCall(self, obj, objtype)


def _wrap_method(cls, name, before=None, after=None):
    """Wrap the functionality the instance- or class-method ``{cls}.{name}`` with ``before`` and
    ``after``.

    This mutates ``cls``, replacing the attribute ``name`` with the new functionality.

    If either ``before`` or ``after`` are given, they should be callables with a compatible
    signature to the method referred to.  They will be called immediately before or after the method
    as appropriate, and any return value will be ignored.
    """
    setattr(cls, name, _WrappedMethod(cls, name, before, after))


def enforce_subclasses_call(methods, attr="_enforce_subclasses_call_cache"):
    """Class decorator which enforces that if any subclasses define on of the ``methods``, they must
    call ``super().<method>()`` or face a ``ValueError`` at runtime.
    This is unlikely to be useful for concrete test classes, who are not normally subclassed.  It
    should not be used on user-facing code, because it prevents subclasses from being free to
    override parent-class behavior, even when the parent-class behavior is not needed.
    This adds behavior to the ``__init__`` and ``__init_subclass__`` methods of the class, in
    addition to the named methods of this class and all subclasses.  The checks could be averted in
    grandchildren if a child class overrides ``__init_subclass__`` without up-calling the decorated
    class's method, though this would typically break inheritance principles.
    Arguments:
        methods:
            Names of the methods to add the enforcement to.  These do not necessarily need to be
            defined in the class body, provided they are somewhere in the method-resolution tree.
        attr:
            The attribute which will be added to all instances of this class and subclasses, in
            order to manage the call enforcement.  This can be changed to avoid clashes.
    Returns:
        A decorator, which returns its input class with the class with the relevant methods modified
        to include checks, and injection code in the ``__init_subclass__`` method.
    """

    methods = {methods} if isinstance(methods, str) else set(methods)

    def initialize_call_memory(self, *_args, **_kwargs):
        """Add the extra attribute used for tracking the method calls."""
        setattr(self, attr, set())

    def save_call_status(name):
        """Decorator, whose return saves the fact that the top-level method call occurred."""

        def out(self, *_args, **_kwargs):
            getattr(self, attr).add(name)

        return out

    def clear_call_status(name):
        """Decorator, whose return clears the call status of the method ``name``.  This prepares the
        call tracking for the child class's method call."""

        def out(self, *_args, **_kwargs):
            getattr(self, attr).discard(name)

        return out

    def enforce_call_occurred(name):
        """Decorator, whose return checks that the top-level method call occurred, and raises
        ``ValueError`` if not.  Concretely, this is an assertion that ``save_call_status`` ran."""

        def out(self, *_args, **_kwargs):
            cache = getattr(self, attr)
            if name not in cache:
                classname = self.__name__ if isinstance(self, type) else type(self).__name__
                raise ValueError(
                    f"Parent '{name}' method was not called by '{classname}.{name}'."
                    f" Ensure you have put in calls to 'super().{name}()'."
                )

        return out

    def wrap_subclass_methods(cls):
        """Wrap all the ``methods`` of ``cls`` with the call-tracking assertions that the top-level
        versions of the methods were called (likely via ``super()``)."""
        # Only wrap methods who are directly defined in this class; if we're resolving to a method
        # higher up the food chain, then it will already have been wrapped.
        for name in set(cls.__dict__) & methods:
            _wrap_method(
                cls,
                name,
                before=clear_call_status(name),
                after=enforce_call_occurred(name),
            )

    def decorator(cls):
        # Add a class-level memory on, so class methods will work as well.  Instances will override
        # this on instantiation, to keep the "namespace" of class- and instance-methods separate.
        initialize_call_memory(cls)
        # Do the extra bits after the main body of __init__ so we can check we're not overwriting
        # anything, and after __init_subclass__ in case the decorated class wants to influence the
        # creation of the subclass's methods before we get to them.
        _wrap_method(cls, "__init__", after=initialize_call_memory)
        for name in methods:
            _wrap_method(cls, name, before=save_call_status(name))
        _wrap_method(cls, "__init_subclass__", after=wrap_subclass_methods)
        return cls

    return decorator


def _iter_loggers():
    """Iterate on existing loggers."""

    # Sadly, Logger.manager and Manager.loggerDict are not documented,
    # but there is no logging public function to iterate on all loggers.

    # The root logger is not part of loggerDict.
    yield logging.getLogger()

    manager = logging.Logger.manager
    for logger in manager.loggerDict.values():
        if isinstance(logger, logging.PlaceHolder):
            continue
        yield logger


@enforce_subclasses_call(["setUp", "setUpClass", "tearDown", "tearDownClass"])
class BaseTestCase(testtools.testcase.WithAttributes, testtools.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__setup_called = False
        self.__teardown_called = False
        self.log_format = "%(asctime)s %(process)d %(levelname)-8s [%(name)s] %(message)s"

    def setUp(self):
        super().setUp()
        if self.__setup_called:
            raise ValueError(
                "In File: %s\n"
                "TestCase.setUp was already called. Do not explicitly call "
                "setUp from your tests. In your own setUp, use super to call "
                "the base setUp." % (sys.modules[self.__class__.__module__].__file__,)
            )
        self.__setup_called = True
        # Setup output fixtures:
        stdout = self.useFixture(fixtures.StringStream("stdout")).stream
        self.useFixture(fixtures.MonkeyPatch("sys.stdout", stdout))
        stderr = self.useFixture(fixtures.StringStream("stderr")).stream
        self.useFixture(fixtures.MonkeyPatch("sys.stderr", stderr))
        # Load configuration
        self.config = None
        self.find_config_file()
        # Configure logging
        default_log_level = None
        module_log_levels = None
        if self.config:
            default_log_level = self.config.config.get("default_log_level", None)
            self.log_format = self.config.config.get("log_format", self.log_format)
            module_log_levels = self.config.config.get("module_log_level", {})
            log_file = self.config.config.get("log_file", None)
            if log_file:
                file_handler = logging.FileHandler(log_file)
                formatter = logging.Formatter(self.log_format)
                file_handler.setFormatter(formatter)
                if default_log_level:
                    file_handler.setLevel(default_log_level)
                logging.getLogger("").addHandler(file_handler)

        self.useFixture(
            fixtures.LoggerFixture(
                nuke_handlers=False, format=self.log_format, level=default_log_level
            )
        )
        if module_log_levels:
            for mod, level in module_log_levels.items():
                logger = logging.getLogger(mod)
                logger.setLevel(level)

        # Set backend
        self.plugin_manager = backend_plugin.BackendPluginManager()
        if self.config:
            backend_script_path = self.config.config.get("backend_script", None)
            backend_selection = self.config.config.get("backend_selection", None)
            if "backend_script" is not None:
                plugin = self.load_plugin_script(backend_script_path)
                self.backend = plugin.get_backend(backend_selection)
            else:
                plugin = self.config.config.get("backend_plugin", "aer")
                self.backends = self.plugin_manager().get_plugin_backends(backend_selection)
                self.backend = self.backends[plugin]
        else:
            self.backends = backend_plugin.BackendPluginManager().get_plugin_backends()
            self.backend = self.backends["aer"]
        # Set test timeout
        test_timeout = os.environ.get("NEKO_TEST_TIMEOUT", 0)
        try:
            test_timeout = int(test_timeout)
        except ValueError:
            test_timeout = 0
        if test_timeout <= 0:
            if self.config is not None:
                test_timeout = self.config.config.get("test_timeout", 0)
        if test_timeout > 0:
            self.useFixture(fixtures.Timeout(test_timeout, gentle=True))

    def load_plugin_script(self, path):
        spec = importlib.util.spec_from_file_location("backend_script", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.main()

    def find_config_file(self):
        env_var = os.getenv("NekoConfigPath", None)
        if env_var is not None:
            if not os.path.isfile(env_var):
                LOG.warning(
                    f"NekoConfigPath environment variable set to {env_var}, however no file "
                    "exists at this path. This value is being ignored."
                )
            else:
                self.config = config.NekoConfig(path)
                return
        default_filename = "neko_config.yml"
        home_dir = os.path.expanduser("~")
        search_locations = [
            os.path.join(os.getcwd(), default_filename),
            os.path.join(home_dir, ".qiskit", default_filename),
            os.path.join(home_dir, ".config", "qiskit-neko", default_filename),
            os.path.join("/etc", default_filename),
        ]
        for path in search_locations:
            if os.path.isfile(path):
                LOG.info(f"Loading configuration file from {path}")
                self.config = config.NekoConfig(path)

    def tearDown(self):
        super().tearDown()
        if self.__teardown_called:
            raise ValueError(
                "In File: %s\n"
                "TestCase.tearDown was already called. Do not explicitly call "
                "tearDown from your tests. In your own tearDown, use super to "
                "call the base tearDown." % (sys.modules[self.__class__.__module__].__file__,)
            )
        self.__teardown_called = True

    def assertDictAlmostEqual(
        self, dict1, dict2, delta=None, msg=None, places=None, default_value=0
    ):
        """Assert two dictionaries with numeric values are almost equal.
        Fail if the two dictionaries are unequal as determined by
        comparing that the difference between values with the same key are
        not greater than delta (default 1e-8), or that difference rounded
        to the given number of decimal places is not zero. If a key in one
        dictionary is not in the other the default_value keyword argument
        will be used for the missing value (default 0). If the two objects
        compare equal then they will automatically compare almost equal.
        Args:
            dict1 (dict): a dictionary.
            dict2 (dict): a dictionary.
            delta (number): threshold for comparison (defaults to 1e-8).
            msg (str): return a custom message on failure.
            places (int): number of decimal places for comparison.
            default_value (number): default value for missing keys.
        Raises:
            TypeError: if the arguments are not valid (both `delta` and
                `places` are specified).
            AssertionError: if the dictionaries are not almost equal.
        """

        error_msg = dicts_almost_equal(dict1, dict2, delta, places, default_value)

        if error_msg:
            msg = self._formatMessage(msg, error_msg)
            raise self.failureException(msg)
