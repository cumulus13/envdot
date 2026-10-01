===========
Auto-Reload
===========

envdot keeps itself in sync with the config file on disk, without you having
to call ``load()`` again or restart the process.

The Smart Default
------------------

Every read from a ``DotEnv`` instance — ``get()``, ``show()``, ``all()``,
``as_dict()``, ``data()``, ``keys()``, attribute access (``env.SOME_KEY``),
``in`` checks (``'KEY' in env``), ``find()``/``find_keys()``/``find_values()``,
``filter()``, and ``search()`` — automatically checks whether the tracked
config file's content changed since the last read, and transparently
reloads it if so:

.. code-block:: python

   from envdot import load_env

   conf = load_env('config.ini')
   conf.show()          # {'TAG_NAME': None, ...}

   # ...edit config.ini on disk, e.g. TAG_NAME = TEST...

   conf.show()          # picks up the change: {'TAG_NAME': 'TEST', ...}
   conf.TAG_NAME         # 'TEST'
   'TAG_NAME' in conf    # True

This is a *cheap* check — a content hash comparison — not a full reparse on
every call, so calling ``get()`` in a hot loop stays fast: the file is only
actually re-read when its hash has changed.

Controlling ``get()``'s Reload Behavior
------------------------------------------

``get()`` (and the ``get_env()`` convenience function) accept a ``reload``
argument:

.. code-block:: python

   from envdot import get_env

   get_env('PORT')                # reload=True (default): checks the file's
                                   # hash and reloads only if it changed
   get_env('PORT', reload=False)  # never check/reload the file this call

There is no separate ``reload`` argument on ``show()``/``all()``/``keys()``/
attribute access/etc. — they always perform the same cheap check.

What Triggers a Reload
--------------------------

* **File content changed** (hash differs from the last read) → reloaded.
* **File is unchanged** → served from memory, no disk read of the config
  content (only a hash comparison).
* **File does not exist / no file is tracked at all** → no crash; reads
  simply return ``None`` / your ``default`` for anything not already known,
  and ``os.environ`` fallback (below) still applies.
* **File is empty (0 bytes) or has no real entries** → loads cleanly to an
  empty configuration, not an error.
* **A file that didn't exist when this ``DotEnv``/``load_env()`` call was
  made, later appears** → **not** auto-discovered on its own. Call
  ``load_env()``/``.load()`` again once you know it exists. (An earlier
  version tried to auto-discover it from inside every read, but combined
  with ``load(override=True)`` that could silently wipe values you'd set
  manually with ``.set()``/``set_env()`` if an unrelated config file
  happened to exist in the current directory — so that part was removed.)
* **The tracked file is deleted after being loaded** → envdot keeps serving
  the last-known-good data rather than crashing or clearing everything.

OS Environment Fallback and Sync
------------------------------------

Independently of file reloading:

* A key that's in ``os.environ`` but was **never** loaded from the config
  file is picked up automatically — this is how a plain
  ``export FOO=bar`` (with no config file involved at all) gets picked up
  by ``get_env('FOO')``, even before ``load_env()`` is ever called.
* If something sets ``os.environ[key] = ...`` **directly** after envdot
  itself already wrote that key to ``os.environ``, ``get()`` picks up the
  new value on the next read:

  .. code-block:: python

     import os
     from envdot import load_env, get_env

     load_env()                    # PORT=8080 from .env
     os.environ['PORT'] = '9999'   # changed directly, outside envdot
     get_env('PORT')                # -> 9999

* A **pre-existing** ``os.environ`` value that envdot never wrote itself
  (left over from another ``DotEnv`` instance, or set before
  ``load_env()`` ran) is **not** silently overridden by a config file
  value envdot just loaded, and does not get treated as "ours to
  refresh" until envdot has written it at least once.
* Pass ``with_os=False`` to ``get()`` to disable this OS-environment
  fallback/sync entirely for a single call.

Reload and ``os.environ`` Stay in Sync on Reload Too
---------------------------------------------------------

When the file changes and a value is reloaded, ``os.environ`` is refreshed
for that key too — as long as envdot itself owns that key in
``os.environ`` (i.e. it wrote it there originally, and nothing external
took over it since). A real, pre-existing external export is never
clobbered by a reload.

For Persistent, Cross-Process Environment Changes
-------------------------------------------------------

Everything above is about the **config file** changing on disk, within the
same running process. If you instead need to detect environment variables
changed **outside the process entirely** — via the Windows registry
(``setx``) or ``/etc/environment`` on Linux — see
:doc:`system-env-watch`, which is a separate, opt-in mechanism.
