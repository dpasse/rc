import os
import sys


def root(directory: str) -> str:
    path = os.path.abspath(os.getcwd())
    while not path.endswith(directory):
        path = os.path.abspath(os.path.join(path, os.pardir))

    return path

def append_path():
    sys.path.append(root('rc'))
