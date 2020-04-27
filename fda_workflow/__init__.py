"""Top-level package for fda-workflow."""

import pkgutil

__author__ = """Justin Payne"""
__email__ = 'justin.payne@fda.hhs.gov'
__version__ = '0.1.0'

# __all__ = ["fda_workflow"]

for loader, module_name, is_pkg in  pkgutil.walk_packages(__path__):
    _module = loader.find_module(module_name).load_module(module_name)
