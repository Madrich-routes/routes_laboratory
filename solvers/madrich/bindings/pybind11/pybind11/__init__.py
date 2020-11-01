from ._version import __version__, version_info  # noqa: F401 imported but unused


def get_include(*args, **kwargs):
    import os
    try:
        from pip import locations
        return os.path.dirname(
            locations.distutils_scheme('pybind11', *args, **kwargs)['headers'])
    except ImportError:
        return 'include'
