# import os
# import json
# import hashlib
# import tempfile

# class EnvStateTracker:
#     def __init__(self, state_file=None):
#         # Safely targets the system's temporary directory to avoid polluting the workspace
#         if state_file is None:
#             self.state_file = os.path.join(tempfile.gettempdir(), "env_tracker_cache.json")
#         else:
#             self.state_file = state_file

#     def _hash_env_dict(self, env_dict):
#         encoded = json.dumps(env_dict, sort_keys=True).encode('utf-8')
#         return hashlib.sha256(encoded).hexdigest()

#     def _load_state(self):
#         if os.path.exists(self.state_file):
#             try:
#                 with open(self.state_file, 'r', encoding='utf-8') as f:
#                     return json.load(f)
#             except json.JSONDecodeError:
#                 pass
#         return {"hash": None, "vars": {}}

#     def _save_state(self, env_hash, env_dict):
#         with open(self.state_file, 'w', encoding='utf-8') as f:
#             json.dump({"hash": env_hash, "vars": env_dict}, f, indent=4, sort_keys=True)

#     def get_changes(self):
#         current_vars = dict(os.environ)
#         current_hash = self._hash_env_dict(current_vars)
        
#         state = self._load_state()

#         if current_hash == state.get("hash"):
#             return {"added": {}, "removed": {}, "modified": {}}

#         old_vars = state.get("vars", {})

#         added = set(current_vars) - set(old_vars)
#         removed = set(old_vars) - set(current_vars)
#         common = set(current_vars) & set(old_vars)

#         changes = {
#             "added": {k: current_vars[k] for k in added},
#             "removed": {k: old_vars[k] for k in removed},
#             "modified": {
#                 k: {'old': old_vars[k], 'new': current_vars[k]} 
#                 for k in common if old_vars[k] != current_vars[k]
#             }
#         }

#         self._save_state(current_hash, current_vars)
#         return changes

# # --- Usage Example ---
# if __name__ == "__main__":
#     tracker = EnvStateTracker()
    
#     # You can verify exactly where it is saving the temp file
#     print(f"Tracking state via: {tracker.state_file}\n")
    
#     changes = tracker.get_changes()
#     if any(changes.values()):
#         print(json.dumps(changes, indent=2))
#     else:
#         print("No changes detected.")


import os
import sys
import json
import hashlib
import tempfile

class DualEnvStateTracker:
    def __init__(self, state_file=None):
        if state_file is None:
            self.state_file = os.path.join(tempfile.gettempdir(), "dual_env_tracker_cache.json")
        else:
            self.state_file = state_file

    def _get_permanent_envs(self):
        """Reads permanent environment variables directly from OS."""
        perm_envs = {}
        
        if sys.platform == "win32":
            import winreg
            # 1. Read System-level permanent variables
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as key:
                    for i in range(1024):
                        try:
                            n, v, t = winreg.EnumValue(key, i)
                            perm_envs[n] = str(v)
                        except OSError:
                            break
            except Exception:
                pass
            
            # 2. Read User-level permanent variables (overwrites system if conflict)
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                    for i in range(1024):
                        try:
                            n, v, t = winreg.EnumValue(key, i)
                            perm_envs[n] = str(v)
                        except OSError:
                            break
            except Exception:
                pass
                
        else:
            # Fallback for Linux/Mac permanent environments
            if os.path.exists("/etc/environment"):
                try:
                    with open("/etc/environment", "r") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                k, v = line.split('=', 1)
                                perm_envs[k.strip()] = v.strip().strip('"').strip("'")
                except Exception:
                    pass
                    
        return perm_envs

    def _hash_state(self, local_dict, perm_dict):
        """Hashes both states to fast-check if anything at all has changed."""
        combined = {"local": local_dict, "perm": perm_dict}
        encoded = json.dumps(combined, sort_keys=True).encode('utf-8')
        return hashlib.sha256(encoded).hexdigest()

    def _load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {"hash": None, "local_vars": {}, "perm_vars": {}}

    def _save_state(self, state_hash, local_vars, perm_vars):
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump({
                "hash": state_hash, 
                "local_vars": local_vars, 
                "perm_vars": perm_vars
            }, f, indent=4, sort_keys=True)

    def _compute_diff(self, old_vars, new_vars):
        added = set(new_vars) - set(old_vars)
        removed = set(old_vars) - set(new_vars)
        common = set(new_vars) & set(old_vars)

        return {
            "added": {k: new_vars[k] for k in added},
            "removed": {k: old_vars[k] for k in removed},
            "modified": {
                k: {'old': old_vars[k], 'new': new_vars[k]} 
                for k in common if old_vars[k] != new_vars[k]
            }
        }

    def get_changes(self):
        # Fetch current states
        current_local = dict(os.environ)
        current_perm = self._get_permanent_envs()
        
        current_hash = self._hash_state(current_local, current_perm)
        state = self._load_state()

        # Fast exit if nothing local or permanent changed
        if current_hash == state.get("hash"):
            return {"added": {}, "removed": {}, "modified": {}}

        # Calculate individual diffs
        local_diff = self._compute_diff(state.get("local_vars", {}), current_local)
        perm_diff = self._compute_diff(state.get("perm_vars", {}), current_perm)

        # Merge diffs - PERMANENT TAKES ABSOLUTE PRECEDENCE
        final_changes = {"added": {}, "removed": {}, "modified": {}}
        processed_keys = set()

        # 1. Apply Permanent changes first
        for category in ["added", "removed", "modified"]:
            for k, v in perm_diff[category].items():
                final_changes[category][k] = v
                processed_keys.add(k)

        # 2. Apply Local changes ONLY IF the key wasn't altered in permanent
        for category in ["added", "removed", "modified"]:
            for k, v in local_diff[category].items():
                if k not in processed_keys:
                    final_changes[category][k] = v

        # Save new state to temp file
        self._save_state(current_hash, current_local, current_perm)
        
        return final_changes


# --- Usage Example ---
if __name__ == "__main__":
    tracker = DualEnvStateTracker()
    print(f"Tracking states via Temp File: {tracker.state_file}\n")
    
    # 1. Check for changes (Local or Permanent OS Registry)
    changes = tracker.get_changes()
    
    if any(changes.values()):
        print("Changes detected (Permanent prioritized over Local):")
        print(json.dumps(changes, indent=2))
    else:
        print("No changes detected in OS Registry or Local environment.")