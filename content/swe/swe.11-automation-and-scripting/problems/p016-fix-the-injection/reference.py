import subprocess
import sys

COUNT = "import sys; print(sum(1 for _ in open(sys.argv[1], encoding='utf-8')))"


def count_lines(filename):
    """Count the lines of a file in a child Python process."""
    result = subprocess.run([sys.executable, "-c", COUNT, str(filename)],
                            capture_output=True, text=True, check=True, timeout=10)
    return int(result.stdout.strip())
