from layer_linter.dependencies import get_dependencies
import os


def test_get_dependencies():
    dirname = os.path.dirname(__file__)
    path = os.path.join(dirname, '..', 'assets')
    os.chdir(path)

    ROOT_PACKAGE = 'flowpackage'
    MODULE_ONE = "{}.one".format(ROOT_PACKAGE)
    MODULE_TWO = "{}.two".format(ROOT_PACKAGE)
    MODULE_THREE = "{}.three".format(ROOT_PACKAGE)
    MODULE_FOUR = "{}.four".format(ROOT_PACKAGE)

    dependencies = get_dependencies(ROOT_PACKAGE)

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
