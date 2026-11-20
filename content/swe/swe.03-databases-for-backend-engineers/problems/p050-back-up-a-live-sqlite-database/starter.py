import shutil


def backup(src_path, dst_path):
    # BUG: a plain file copy is not safe while someone writes to the database
    shutil.copyfile(src_path, dst_path)
