from layer_linter.dependencies import DependencyGraph
from layer_linter.module import Module, SafeFilenameModule
import os
import sys


def test_dependency_graph():
    dirname = os.path.dirname(__file__)
    path = os.path.abspath(os.path.join(dirname, '..', '..', 'assets'))

    sys.path.append(path)

    ROOT_PACKAGE = 'dependenciespackage'
    MODULE_ONE = Module("{}.one".format(ROOT_PACKAGE))
    MODULE_TWO = Module("{}.two".format(ROOT_PACKAGE))
    MODULE_THREE = Module("{}.three".format(ROOT_PACKAGE))
    MODULE_FOUR = Module("{}.four".format(ROOT_PACKAGE))

    SUBPACKAGE = 'subpackage'
    SUBMODULE_ONE = Module("{}.{}.one".format(ROOT_PACKAGE, SUBPACKAGE))
    SUBMODULE_TWO = Module("{}.{}.two".format(ROOT_PACKAGE, SUBPACKAGE))
    SUBMODULE_THREE = Module("{}.{}.three".format(ROOT_PACKAGE, SUBPACKAGE))

    SUBSUBPACKAGE = 'subsubpackage'
    SUBSUBMODULE_ONE = Module("{}.{}.{}.one".format(ROOT_PACKAGE, SUBPACKAGE, SUBSUBPACKAGE))
    SUBSUBMODULE_TWO = Module("{}.{}.{}.two".format(ROOT_PACKAGE, SUBPACKAGE, SUBSUBPACKAGE))
    SUBSUBMODULE_THREE = Module("{}.{}.{}.three".format(ROOT_PACKAGE, SUBPACKAGE, SUBSUBPACKAGE))

    root_package = __import__(ROOT_PACKAGE)
    graph = DependencyGraph(
        SafeFilenameModule(name=ROOT_PACKAGE, filename=root_package.__file__)
    )

    assert graph.find_path(
        upstream=MODULE_ONE,
        downstream=MODULE_TWO) == (MODULE_TWO, MODULE_ONE)

    assert graph.find_path(
        upstream=MODULE_TWO,
        downstream=MODULE_ONE) is None

    assert graph.find_path(
        upstream=MODULE_ONE,
        downstream=MODULE_FOUR) == (MODULE_FOUR, MODULE_THREE,
                                    MODULE_TWO, MODULE_ONE)

    assert graph.find_path(
        upstream=SUBMODULE_ONE,
        downstream=SUBMODULE_THREE) == (SUBMODULE_THREE, SUBMODULE_TWO, SUBMODULE_ONE)

    assert graph.find_path(
        upstream=SUBSUBMODULE_ONE,
        downstream=SUBSUBMODULE_THREE) == (SUBSUBMODULE_THREE, SUBSUBMODULE_TWO, SUBSUBMODULE_ONE)

    # Module count should be 13 (running total in square brackets):
    # - dependenciespackage [1]
    #   - one [2]
    #   - two [3]
    #   - three [4]
    #   - four [5]
    #   - .hidden [X]
    #   - migrations [X]
    #   - subpackage [6]
    #     - one [7]
    #     - two [8]
    #     - three [9]
    #     - is [10] (treat reserved keywords as normal modules)
    #     - subsubpackage [11]
    #       - one [12]
    #       - two [13]
    #       - three [14]
    assert graph.module_count == 14
    # Dependency count should be 7:
    # dependenciespackage.two <- dependenciespackage.one
    # dependenciespackage.three <- dependenciespackage.two
    # dependenciespackage.four <- dependenciespackage.three
    # dependenciespackage.subpackage.two <- dependenciespackage.subpackage.one
    # dependenciespackage.subpackage.three <- dependenciespackage.subpackage.two
    # dependenciespackage.subpackage.is <- dependenciespackage.subpackage.three
    # dependenciespackage.subpackage.subsubpackage.two
    #           <- dependenciespackage.subpackage.subsubpackage.one
    # dependenciespackage.subpackage.subsubpackage.three
    #           <- dependenciespackage.subpackage.subsubpackage.two
    assert graph.dependency_count == 8
