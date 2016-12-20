from unittest.mock import patch as stdlib_patch

from tdubs import Spy, Stub


def spy(path, **kwargs):
    kwargs.setdefault('new', Spy())
    return stdlib_patch(path, **kwargs)


def stub(path, **kwargs):
    kwargs.setdefault('new', Stub())
    return stdlib_patch(path, **kwargs)
