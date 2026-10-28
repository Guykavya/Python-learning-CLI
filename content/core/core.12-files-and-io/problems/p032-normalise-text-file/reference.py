def normalise_text_file(src, dst):
    with open(src, encoding="utf-8-sig") as f:
        text = f.read()
    with open(dst, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return len(text.splitlines())
