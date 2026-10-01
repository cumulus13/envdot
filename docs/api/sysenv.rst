========================
System Environment Watch
========================

.. module:: envdot.sysenv
   :synopsis: Detect persistent (registry / env-file) environment changes made outside the process

See :doc:`../usage/system-env-watch` for a full usage guide. This page is
the API reference for the underlying watcher, in case you want to use it
independently of :class:`envdot.DotEnv`.

SystemEnvWatcher
------------------

.. class:: SystemEnvWatcher(ignore=('PATH',), min_interval=0.25, backend=None)

   Polls the persistent environment store (Windows registry, or Linux
   env files) and reports what changed since the last poll.

   :param ignore: Variable names never reported (matched case-insensitively
      on Windows). Defaults to ``('PATH',)`` since the process ``PATH`` is
      a merge of multiple sources.
   :type ignore: Iterable[str]
   :param min_interval: Minimum seconds between actual store checks
      (default: ``0.25``). A ``poll()`` call within this window returns
      immediately with no changes, without touching the registry/filesystem.
   :type min_interval: float
   :param backend: Override the platform-detected backend (mainly useful
      for testing). Defaults to the Windows registry backend on Windows,
      the Linux env-file backend on Linux, and ``None`` (unsupported)
      elsewhere.

   .. attribute:: supported

      ``True`` if this watcher has a usable backend for the current
      platform, ``False`` otherwise.

      :type: bool

   .. method:: poll(force=False)

      Check the persistent store for changes since the last poll.

      :param force: Bypass the ``min_interval`` throttle and check now.
      :type force: bool
      :returns: A ``(changed, removed)`` tuple:

         * ``changed`` — ``{name: new_value}`` for variables added or
           modified.
         * ``removed`` — ``{name: last_known_value}`` for variables that
           disappeared from the store.

         The **first** successful poll only records a baseline and always
         returns ``({}, {})`` — the running process already has the
         environment it started with, so nothing "changed" relative to
         that baseline yet.
      :rtype: tuple[dict, dict]

   **Example:**

   .. code-block:: python

      from envdot.sysenv import SystemEnvWatcher

      watcher = SystemEnvWatcher(ignore=('PATH',), min_interval=0.25)

      if watcher.supported:
          watcher.poll(force=True)           # establish baseline
          ...
          changed, removed = watcher.poll()
          for name, value in changed.items():
              print(f"{name} changed to {value!r}")

Errors are swallowed defensively: if the registry or env files become
briefly unreadable (permissions, a file mid-write, etc.), ``poll()``
returns ``({}, {})`` rather than raising, so a transient glitch in the
persistent store never breaks a normal read.

Platform Backends
--------------------

These are implementation details — normally you only interact with
:class:`SystemEnvWatcher` — but they're documented here for anyone
writing a custom ``backend=``.

.. class:: _WindowsRegistryBackend(winreg_module=None)

   Reads ``HKEY_LOCAL_MACHINE\...\Session Manager\Environment`` and
   ``HKEY_CURRENT_USER\Environment``. Only ``REG_SZ`` and ``REG_EXPAND_SZ``
   values are read; other registry value types are ignored. Names are
   upper-cased (Windows variable names are case-insensitive), and the
   user hive is applied after the system hive, so a name defined in both
   resolves to the user's value — matching how Windows itself resolves it.

.. class:: _PosixFileBackend(paths=None)

   Reads ``/etc/environment`` and ``~/.config/environment.d/*.conf`` by
   default (glob patterns; pass your own list of paths/patterns to
   override). Parses simple ``KEY=VALUE`` lines, with ``#`` comments, an
   optional leading ``export``, and surrounding quotes stripped.

   .. staticmethod:: parse(text)

      Parse the contents of one such file into a ``{key: value}`` dict.
      Exposed as a ``staticmethod`` mainly for testing.
