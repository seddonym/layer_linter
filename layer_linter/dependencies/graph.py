import logging
from typing import List, Optional
import networkx  # type: ignore
from networkx.algorithms import shortest_path  # type: ignore

from ..module import Module, SafeFilenameModule
from .path import ImportPath
from .scanner import PackageScanner
from .analysis import DependencyAnalyzer


logger = logging.getLogger(__name__)


class InvalidDependencies(Exception):
    pass


class DependencyGraph:
    """
    A graph of the internal dependencies in a Python package.

    Usage:
        package = __import__('mypackage')

        graph = DependencyGraph(package)

        path = graph.find_path(
            downstream='',
            upstream='',
            ignore_paths=[
                ImportPath(
                    importer='mypackage.foo',
                    imported='mypackage.bar.baz'
                ),
            ]
        )

        descendants = graph.get_descendants('mypackage.foo')
    """
    def __init__(self, package: SafeFilenameModule) -> None:
        scanner = PackageScanner(package)
        self.modules = scanner.scan_for_modules()

        self._networkx_graph = networkx.DiGraph()
        self.dependency_count = 0

        # TODO include handling of syntax errors, which should be included in
        # a raise of InvalidDependencies - the method we use will determine when this
        # is handled.
        analyzer = DependencyAnalyzer(modules=self.modules, package=package)
        for import_path in analyzer.determine_import_paths():
            self._add_path_to_networkx_graph(import_path)
            self.dependency_count += 1

        self.module_count = len(self.modules)

    def find_path(self,
                  downstream: Module, upstream: Module,
                  ignore_paths: Optional[List[ImportPath]] = None) -> List[str]:
        """
        Args:
            downstream (string):                 Absolute name of module.
            upstream (string)                    Absolute name of module.
            ignore_paths
                (list of ImportPaths, optional): List of the paths that should not be considered.

        Returns:
            List of module names showing the dependency path between
            the downstream and the upstream module, or None if there
            is no dependency.

            For example, given an upstream module 'alpha' and a downstream
            module 'delta':

                - ['alpha'] will be returned if delta directly imports alpha.
                - ['delta', 'gamma', 'beta', 'alpha'] will be returned if delta imports
                  gamma, which imports beta, which imports alpha.
        """
        logger.debug("Finding path from '{}' up to '{}'.".format(downstream, upstream))
        ignore_paths = ignore_paths if ignore_paths else []

        removed_paths = self._remove_paths_from_networkx_graph(ignore_paths)

        try:
            path = shortest_path(self._networkx_graph, downstream, upstream)
        except (networkx.NetworkXNoPath, networkx.exception.NodeNotFound):
            # Either there is no path, or one of the modules doesn't even exist.
            path = None
        else:
            path = tuple(path)

        self._restore_paths_to_networkx_graph(removed_paths)

        return path

    def get_descendants(self, module: Module) -> List[Module]:
        """
        Returns:
            List of modules that are within the supplied module.
        """
        descendants: List[Module] = []
        for candidate in self.modules:
            if candidate.name.startswith('{}.'.format(module.name)):
                descendants.append(candidate)
        return descendants

    def _add_path_to_networkx_graph(self, import_path: ImportPath) -> None:
        self._networkx_graph.add_edge(import_path.importer, import_path.imported)

    def _remove_path_from_networkx_graph(self, import_path: ImportPath) -> None:
        self._networkx_graph.remove_edge(import_path.importer, import_path.imported)

    def _import_path_is_in_networkx_graph(self, import_path: ImportPath) -> bool:
        return self._networkx_graph.has_successor(
            import_path.importer, import_path.imported
        )

    def _remove_paths_from_networkx_graph(
        self, import_paths: List[ImportPath]
    ) -> List[ImportPath]:
        """
        Given a list of ImportPaths, remove any that exist from the graph.

        Returns:
             List of removed ImportPaths.
        """
        removed_paths = []
        for import_path in import_paths:
            if self._import_path_is_in_networkx_graph(import_path):
                self._remove_path_from_networkx_graph(import_path)
                removed_paths.append(import_path)
        return removed_paths

    def _restore_paths_to_networkx_graph(self, import_paths: List[ImportPath]) -> None:
        for import_path in import_paths:
            self._add_path_to_networkx_graph(import_path)
