import os
import platform
import sys

print("Executable:", sys.executable)
print("Version:", platform.python_version())
print("Implementation:", platform.python_implementation())
print("System:", platform.system())
print("Folder:", os.getcwd())
