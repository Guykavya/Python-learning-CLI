def lint_message(msg):
    if not msg.strip():
        return ["empty"]
    lines = msg.rstrip().split("\n")
    problems = []
    if len(lines[0]) > 50:
        problems.append("subject-too-long")
    if lines[0].endswith("."):
        problems.append("subject-ends-with-period")
    if len(lines) > 1 and lines[1] != "":
        problems.append("no-blank-line")
    if any(len(line) > 72 for line in lines[1:]):
        problems.append("body-line-too-long")
    return problems
