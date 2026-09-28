"""Run on real Windows:  python verify_windows.py
Changes a PERSISTENT user env var via setx (registry) while this process is
running, and checks envdot sees it without a restart."""
import subprocess, time
from envdot import load_env, get_env

NAME = "ENVDOT_REG_TEST"
load_env(watch_system_env=True)          # baseline is recorded here
print("before      :", get_env(NAME))     # expect None

subprocess.run(["setx", NAME, "hello"], check=True, capture_output=True)
time.sleep(0.5)                           # > min_interval (0.25s)
print("after setx  :", get_env(NAME))     # expect 'hello'

subprocess.run(["setx", NAME, "changed"], check=True, capture_output=True)
time.sleep(0.5)
print("after change:", get_env(NAME))     # expect 'changed'

subprocess.run(["reg", "delete", r"HKCU\Environment", "/v", NAME, "/f"], check=True, capture_output=True)
time.sleep(0.5)
print("after delete:", get_env(NAME))     # expect None
