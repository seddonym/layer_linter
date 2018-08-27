1 / 0  # Check that Runtime errors don't prevent this from being analyzed.

from differentimporttypes.one import alpha  # Import from: absolute import of module.
from differentimporttypes import one  # Import from: absolute import of package.

from . import beta  # Import from: relative, same level, module.
from . import gamma  # Import from: relative, same level, package

from .gamma import foo  # Import from: relative, down a level, module.

from ..two import alpha  # Import from: relative, up a level, module.

from .delta import some_function  # Import from: a function. NOT SUPPORTED YET.

def wrapper():
    from . import epsilon  # Import from: inside a function.


import differentimporttypes.three  # Import: absolute import of package.
import differentimporttypes.four.alpha  # Import: absolute import of module.

# Check that imports from other packages aren't included.
import pytest
from pytest import mark
