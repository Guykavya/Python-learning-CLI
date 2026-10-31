import configparser


def read_ini(path):
    cp = configparser.ConfigParser()
    cp.read(path, encoding="utf-8")
    return {section: dict(cp[section]) for section in cp.sections()}


def get_int(path, section, option, fallback):
    cp = configparser.ConfigParser()
    cp.read(path, encoding="utf-8")
    return cp.getint(section, option, fallback=fallback)
