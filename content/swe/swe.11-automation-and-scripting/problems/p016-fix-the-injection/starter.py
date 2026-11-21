import subprocess
import sys

COUNT = "import sys; print(sum(1 for _ in open(sys.argv[1], encoding='utf-8')))"


def count_lines(filename):
    """Count the lines of a file in a child Python process."""
    # BUG: the file name is pasted into a shell command string.
    command = '"' + sys.executable + '" -c "' + COUNT + '" ' + str(filename)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return int(result.stdout.split()[0])
