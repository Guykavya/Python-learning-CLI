def copy_blocks(src, dst, block_size):
    blocks = 0
    with open(src, "rb") as fin, open(dst, "wb") as fout:
        while True:
            block = fin.read(block_size)
            if not block:
                break
            fout.write(block)
            blocks += 1
    return blocks
