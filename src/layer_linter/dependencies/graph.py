import logging
from typing import List, Optional, Any
import networkx  # type: ignore
from networkx.algorithms import shortest_path  # type: ignore
import grimp

from ..module import Module, SafeFilenameModule
from .path import ImportPath
from .scanner import PackageScanner
from .analysis import DependencyAnalyzer


logger = logging.getLogger(__name__)


class DependencyGraph:
    """
    A graph of the internal dependencies in a Python package.

    Usage:
        graph = DependencyGraph(
            SafeFilenameModule('mypackage', '/path/to/mypackage/__init__.py')
        )

        path = graph.find_path(
            downstream=Module('mypackage.foo.one'),
            upstream=Module('mypackage.bar.two'),
            ignore_paths=[
                ImportPath(
                    importer=Module('mypackage.foo'),
                    imported=Module('mypackage.baz.three'),
                ),
            ]
        )

        descendants = graph.get_descendants(Module('mypackage.foo'))
    """
    def __init__(self, package: SafeFilenameModule) -> None:
        self._grimp_graph = grimp.build_graph(package.name)
        self.modules = [Module(m) for m in self._grimp_graph.modules]
        self.module_count = len(self.modules)
        self.dependency_count = 99 # TODO

    def get_modules_directly_imported_by(self, importer: Module) -> List[Module]:
        """
        Returns all the modules directly imported by the importer.
        """
        return list(
            self._grimp_graph.find_modules_directly_imported_by(importer.name)
        )

    def find_path(self,
                  downstream: Module, upstream: Module,
                  ignore_paths: Optional[List[ImportPath]] = None) -> List[Module]:
        """
        Find a list of module names showing the dependency path between the downstream and the
        upstream module, or None if there is no dependency.

        For example, given an upstream module a and a downstream module d:

                - [d, a] will be returned if d directly imports a.
                - [d, c, b, a] will be returned if d imports c, which imports b, which imports a.
                - None will be returned if d does not import a (even indirectly).
        """
        logger.debug("Finding path from '{}' up to '{}'.".format(downstream, upstream))
        ignore_paths = ignore_paths if ignore_paths else []

        removed_paths = self._remove_paths_from_grimp_graph(ignore_paths)
        if not all([
            upstream.name in self._grimp_graph.modules,
            downstream.name in self._grimp_graph.modules,
        ]):
            return None

        path = self._grimp_graph.find_shortest_chain(
            importer=downstream.name,
            imported=upstream.name,
        )

        self._restore_paths_to_grimp_graph(removed_paths)

        if path:
            return [Module(m) for m in path]
        else:
            return None

    def get_descendants(self, module: Module) -> List[Module]:
        """
        Returns:
            List of modules that are within the supplied module.
        """
        return list(self._grimp_graph.find_descendants(module.name))

    def _remove_paths_from_grimp_graph(
        self, import_paths: List[ImportPath]
    ) -> List[ImportPath]:
        """
        Given a list of ImportPaths, remove any that exist from the graph.

        Returns:
             List of removed ImportPaths.
        """
        removed_paths = []
        for import_path in import_paths:
            if self._grimp_graph.direct_import_exists(
                importer=import_path.importer.name,
                imported=import_path.imported.name
            ):
                self._grimp_graph.remove_import(importer=import_path.importer.name,
                                                imported=import_path.imported.name)
                removed_paths.append(import_path)
        return removed_paths

    def _restore_paths_to_grimp_graph(self, import_paths: List[ImportPath]) -> None:
        for import_path in import_paths:
            self._grimp_graph.add_import(importer=import_path.importer.name,
                                         imported=import_path.imported.name)

    def __contains__(self, item: Any) -> bool:
        """
        Returns whether or not the given item is a Module in the dependency graph.

        Usage:
            if module in graph:
                ...
        """
        return item in self.modules
