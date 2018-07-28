from layer_linter.dependencies import get_dependencies
import os
import sys


def test_get_dependencies():
    dirname = os.path.dirname(__file__)
    path = os.path.abspath(os.path.join(dirname, '..', 'assets'))

    sys.path.append(path)

    ROOT_PACKAGE = 'dependenciespackage'
    MODULE_ONE = "{}.one".format(ROOT_PACKAGE)
    MODULE_TWO = "{}.two".format(ROOT_PACKAGE)
    MODULE_THREE = "{}.three".format(ROOT_PACKAGE)
    MODULE_FOUR = "{}.four".format(ROOT_PACKAGE)

    SUBPACKAGE = 'subpackage'
    SUBMODULE_ONE = "{}.{}.one".format(ROOT_PACKAGE, SUBPACKAGE)
    SUBMODULE_TWO = "{}.{}.two".format(ROOT_PACKAGE, SUBPACKAGE)
    SUBMODULE_THREE = "{}.{}.three".format(ROOT_PACKAGE, SUBPACKAGE)

    SUBSUBPACKAGE = 'subsubpackage'
    SUBSUBMODULE_ONE = "{}.{}.{}.one".format(ROOT_PACKAGE, SUBPACKAGE, SUBSUBPACKAGE)
    SUBSUBMODULE_TWO = "{}.{}.{}.two".format(ROOT_PACKAGE, SUBPACKAGE, SUBSUBPACKAGE)
    SUBSUBMODULE_THREE = "{}.{}.{}.three".format(ROOT_PACKAGE, SUBPACKAGE, SUBSUBPACKAGE)

    root_package = __import__(ROOT_PACKAGE)
    dependencies = get_dependencies(root_package)

    assert dependencies.find_path(
        upstream=MODULE_ONE,
        downstream=MODULE_TWO) == (MODULE_TWO, MODULE_ONE)

    assert dependencies.find_path(
        upstream=MODULE_TWO,
        downstream=MODULE_ONE) == None

    assert dependencies.find_path(
        upstream=MODULE_ONE,
        downstream=MODULE_FOUR) == (MODULE_FOUR, MODULE_THREE,
                                    MODULE_TWO, MODULE_ONE)

    assert dependencies.find_path(
        upstream=SUBMODULE_ONE,
        downstream=SUBMODULE_THREE) == (SUBMODULE_THREE, SUBMODULE_TWO, SUBMODULE_ONE)

    assert dependencies.find_path(
        upstream=SUBSUBMODULE_ONE,
        downstream=SUBSUBMODULE_THREE) == (SUBSUBMODULE_THREE, SUBSUBMODULE_TWO, SUBSUBMODULE_ONE)
