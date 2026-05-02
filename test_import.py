import os
os.environ["UNSLOTH_COMPILE_DISABLE"] = "1"

import sys

# Try importing unsloth piece by piece to find the crash
modules = [
    "unsloth._utils",
    "unsloth.models",
    "unsloth.save",
    "unsloth.chat_templates",
]

for mod in modules:
    try:
        __import__(mod)
        print(f"  {mod}: OK", flush=True)
    except ImportError as e:
        print(f"  {mod}: ImportError - {e}", flush=True)
    except Exception as e:
        print(f"  {mod}: {type(e).__name__} - {e}", flush=True)

print("Trying top-level unsloth...", flush=True)
try:
    import unsloth
    print(f"  unsloth: OK, version={unsloth.__version__}", flush=True)
except Exception as e:
    print(f"  unsloth: {type(e).__name__} - {str(e)[:200]}", flush=True)

print("DONE", flush=True)