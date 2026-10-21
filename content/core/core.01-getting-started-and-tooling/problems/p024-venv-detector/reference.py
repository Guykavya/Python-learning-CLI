import sys

print("Executable:", sys.executable)
print("Prefix:", sys.prefix)
print("Base prefix:", sys.base_prefix)
print("In virtual environment:", sys.prefix != sys.base_prefix)
