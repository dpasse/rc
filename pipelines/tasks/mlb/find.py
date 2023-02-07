import os


def root():
    path = os.path.abspath(os.getcwd())
    while not path.endswith('rc'):
        path = os.path.abspath(os.path.join(path, os.pardir))

    return path
