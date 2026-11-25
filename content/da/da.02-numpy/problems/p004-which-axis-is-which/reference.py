import numpy as np


def column_means(a):
    return a.mean(axis=0)


def row_maxes(a):
    return a.max(axis=1)


def per_image_mean(stack):
    return stack.mean(axis=(1, 2))
