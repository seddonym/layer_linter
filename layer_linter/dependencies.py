import logging
from pydeps.py2depgraph import _create_dummy_module, MyModuleFinder
import networkx
from networkx.algorithms import shortest_path
import sys
import os

logger = logging.getLogger(__name__)


def get_dependencies(package_name):
    return DependencyGraph(package_name)


class DependencyGraph:
    def __init__(self, package_name):
        self.package_name = package_name
        sources = self._generate_pydep_sources()
        self._build_networkx_graph_from_sources(sources)
        pass

    def _generate_pydep_sources(self):
        dummy_module = _create_dummy_module(self.package_name, verbose=None)
        path = sys.path[:]
        path.insert(0, os.path.dirname(dummy_module))

        finder = MyModuleFinder(path)
        finder.run_script(dummy_module)

        # Remove dummy file
        os.unlink(dummy_module)

        self._sources = finder._depgraph
        return self._sources

    def _build_networkx_graph_from_sources(self, sources):
        self._networkx_graph = networkx.DiGraph()
        self.module_count = 0
        self.dependency_count = 0
        for module_name, imported_modules in sources.items():
            # TODO: We only add internal modules to the networkx graph,
            # but it would be much better if we never added them to the pydep graph.
            if module_name.startswith(self.package_name):
                self.module_count += 1
                for upstream_module in imported_modules:
                    if upstream_module.startswith(self.package_name):
                        self._networkx_graph.add_edge(module_name, upstream_module)
                        self.dependency_count += 1
                        logger.debug("Added edge from '{}' to '{}'.".format(
                            module_name, upstream_module))

    def find_path(self, downstream, upstream):
        """
        Args:
            downstream (string) - absolute name of module.
            upstream (string)- absolute name of module.
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
        try:
            path = shortest_path(self._networkx_graph, downstream, upstream)
        except (networkx.NetworkXNoPath, networkx.exception.NodeNotFound):
            # Either there is no path, or one of the modules doesn't even exist.
            return None
        else:
            return tuple(path)

    def get_descendants(self, module):
        """
        Args:
            module (string): absolute name of module.
        Returns:
            List of modules that are within that module (string).
        """
        descendants = []
        for candidate in self._sources.keys():
            if candidate.startswith('{}.'.format(module)):
                descendants.append(candidate)
        return descendants
