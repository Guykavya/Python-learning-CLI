import yaml


def check_compose(yaml_text):
    # TODO: parse, find the dependencies, apply the five rules of problem.md
    data = yaml.safe_load(yaml_text)
    return []
