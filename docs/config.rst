Qiskit-Neko Configuration Files
===============================

To support running against different backends and also tune the execute of
tests qiskit-neko supports configuration files to tweak the configuration
and make reproducible testing simpler. The format for qiskit-neko's
configuration is a [yaml](https://yaml.org/) file, a fully populated example
is below

```yaml
---
test_timeout: 60.0
backend_plugin: ibmq
backend_selection: santiago
backend_script: /tmp/backend_script
```

The options are defined as below:

* ``test_timeout`` - A float value in seconds for the maximum per test timeout
  value. If a test takes longer than this value in seconds it will be marked
  as error/failed and the rest of the suite will run
* ``backend_plugin`` - A string value that takes in the plugin name to use for
  backends.  If this is not specified the backend plugin will default to the
  included :class:`.AerPlugin` class.
* ``backend_selection`` - An selection string that will be passed to the
  configured plugin and will be used to influence the returned backend from the
  backend. Refer to the plugin documentation for how this can be used as the
  exact behavior will be based on the plugin in use.
* ``backend_script`` - An optional absolute path to a script file to run in lieu
  of a plugin. This script file will be imported from this configured path.
  It must contain a function in the script named ``main()`` which when called
  returns a :class:`qiskit_neko.backend_plugin.BackendPlugin` subclass object
  that can be used for the tests.

Specifying Configuration Files
------------------------------

By default the the configuration file for qiskit-neko is looked for in 4 places
in the following order. If a file is found in that location it will be used and
none of the subsequent locations will be checked:

#. $CWD/neko_config.yml
#. ~/.qiskit/neko_config.yml
#. ~/.config/qiskit-neko/neko_config.yml
#. /etc/neko_config.yml

Since the actual execution of tests is handled by the external Python standard
library [unittest](https://docs.python.org/3/library/unittest.html) framework
the only mechanism to excplictly specify a configuration file path is with an
environment variable. You can set the environment variable ``NekoConfigPath`` to
the absolute path to the configuration file. If this is specified it will be
used regardless of a file being present in any of the default file locations.
