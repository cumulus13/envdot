========================================
System Environment Watching (Persistent)
========================================

.. note::

   This is a newer addition — see :doc:`../changelog` (Unreleased).

A running process only has the environment variables it started with.
Changing a variable **persistently** — via ``setx`` or the Windows System
Properties dialog on Windows, or by editing ``/etc/environment`` on Linux —
is written to a persistent store (the registry, or a file), and a process
that's already running never sees it, no matter how many times you call
``os.getenv()``.

envdot's ``sysenv`` module closes that gap: it polls the persistent store
for changes and applies exactly what changed to the running process, on
top of the file-based :doc:`auto-reload`.

This is **off by default** — nothing is polled or applied unless you
explicitly turn it on.

Enabling It
-----------

.. code-block:: python

   from envdot import load_env, get_env

   # Turn it on at load time...
   conf = load_env(watch_system_env=True)

   # ...or on an existing instance
   conf.enable_system_watch()

   get_env('SOME_VAR')   # now reflects registry/env-file changes too

``enable_system_watch()`` returns ``True`` if the current platform is
supported, ``False`` otherwise (it's always safe to call — unsupported
platforms are a clean no-op, never an error):

.. code-block:: python

   supported = conf.enable_system_watch()
   if not supported:
       print("Persistent env watching isn't available on this platform")

Turn it off again with ``conf.disable_system_watch()``.

What Gets Applied, and When
-------------------------------

* **Only what actually changed** since the watch was enabled (or since the
  last poll) is applied — a value you set inside the process is never
  overwritten by an unrelated change elsewhere in the store.
* The state **at the moment you call** ``enable_system_watch()`` /
  ``watch_system_env=True`` is the baseline. A change made *before* that
  point is not retroactively applied.
* Applied changes land in ``os.environ`` *and* in envdot's own data, so
  ``get()``, ``show()``, attribute access, and your patched ``os.getenv()``
  all see them.
* A variable **removed** from the persistent store is only removed from
  the process if envdot itself applied it and nothing changed it
  in-process since — a local override is never deleted this way.
* Polling is throttled (default: every 0.25s at most) so checking on every
  ``get()`` call in a hot loop stays cheap.

.. code-block:: python

   import os, time
   from envdot import load_env, get_env

   conf = load_env(watch_system_env=True)
   print(get_env('MY_VAR'))     # None

   # ...on Windows: `setx MY_VAR hello`  (or via System Properties)
   # ...on Linux:   edit /etc/environment, add MY_VAR=hello

   time.sleep(0.3)              # give the poll interval a moment
   print(get_env('MY_VAR'))     # 'hello' - no restart needed

Windows
-------

Reads two registry locations, in this order (later wins for the same
name, matching how Windows itself resolves duplicates):

1. ``HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment``
   (system-wide variables)
2. ``HKEY_CURRENT_USER\Environment`` (per-user variables)

Change detection uses each key's registry *last-write timestamp*, so a
poll that finds nothing changed is two cheap registry calls, not a full
re-read. ``REG_EXPAND_SZ`` values (e.g. ``%JAVA_HOME%\bin``) are expanded
against the other values just read plus the current process environment.
Variable names are matched case-insensitively, as Windows itself does.

``PATH`` is **ignored by default** (see below) since the process ``PATH``
is a merge of the system and user ``PATH`` plus whatever the parent
process injected — blindly replacing it with one registry value would
break it.

Linux
-----

Reads, in order:

1. ``/etc/environment``
2. ``~/.config/environment.d/*.conf``

Both are simple ``KEY=VALUE`` files (``#`` comments and an optional
leading ``export`` are supported; quoted values have their quotes
stripped). Change detection uses each file's mtime + size.

.. note::

   Shell startup files such as ``~/.bashrc`` or ``~/.profile`` are
   **deliberately not read** — they are scripts, and parsing or executing
   them to extract variables is unsafe and format-fragile. Put persistent
   variables in ``/etc/environment`` or a ``~/.config/environment.d/*.conf``
   file instead (the mechanism ``systemd`` and most desktop session
   managers already use).

macOS and Other Platforms
------------------------------

Not currently supported. ``enable_system_watch()`` returns ``False`` and
does nothing further — your code keeps working normally, it just won't
see persistent changes made outside the process. (The real mechanism on
macOS is ``launchctl setenv``/``getenv``, which works per-variable rather
than as an enumerable store, so supporting it needs an explicit list of
variable names to watch — this can be added if you need it.)

Customizing What's Watched
--------------------------------

.. code-block:: python

   # Watch PATH too (off by default - see the Windows section above)
   conf.enable_system_watch(ignore=())

   # Poll at most once every 2 seconds instead of every 0.25s
   conf.enable_system_watch(min_interval=2.0)

Using ``SystemEnvWatcher`` Directly
----------------------------------------

For advanced use (e.g. watching independently of a ``DotEnv`` instance):

.. code-block:: python

   from envdot.sysenv import SystemEnvWatcher

   watcher = SystemEnvWatcher(ignore=('PATH',), min_interval=0.25)

   if watcher.supported:
       watcher.poll(force=True)          # record the baseline
       ...
       changed, removed = watcher.poll()  # {name: value}, {name: last_value}

See :doc:`../api/sysenv` for the full API reference.
