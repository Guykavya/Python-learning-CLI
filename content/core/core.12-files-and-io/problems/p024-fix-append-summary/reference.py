def append_summary(src, dst):
    with open(src, encoding="utf-8") as f:
        count = sum(1 for line in f if "ERROR" in line)
    with open(dst, "a", encoding="utf-8") as out:
        out.write(f"errors={count}\n")
    return count
