from importlib.metadata import version

from .api import Device  # noqa: F401

__version__ = version(__package__)
