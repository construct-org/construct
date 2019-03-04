import os

this_dir = os.path.abspath(os.path.dirname(__file__))


def test_path(*paths):
    return os.path.join(this_dir, *paths).replace('\\', '/')
