def append_summary(src, dst):
    f = open(src, encoding="utf-8")
    count = 0
    for line in f:
        if line.startswith("ERROR"):
            count += 1
    out = open(dst, "w", encoding="utf-8")
    out.write(f"errors={count}")
    return count
