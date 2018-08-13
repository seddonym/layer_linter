import logging
from keyword import iskeyword
from pydeps.py2depgraph import (
    MyModuleFinder as PydepsModuleFinder,
    pysource as is_python_file)
import networkx
from networkx.algorithms import shortest_path
import sys
import os

logger = logging.getLogger(__name__)


def get_dependencies(package_name):
    return DependencyGraph(package_name)


class InternalModuleFinder(PydepsModuleFinder):
    """
    Analyses the internal dependencies for a Python package.

    The API is a bit unintuitive. You instantiate the module finder with the Python package
    that you want to analyse:
         package = __import__('mypackage')
        finder = InternalModuleFinder(package)

    Then you pass `run_script` the name of a Python module, built elsewhere, that contains imports
    of all the modules within that package:

         finder.run_script('path/to/dummy_module.py')

    Finally you can access a dictionary containing all the import information for each imported
    module:
         depgraph = finder._depgraph
     This is very much an interim approach, leveraging the work of the Pydeps package. At some point
    we should simplify this, which will probably remove the need for Pydeps as a dependency.
    We can probably use modulefinder.ModuleFinder from the standard library.
    """
    def __init__(self, *args, package, **kwargs):
        self.package = package
        kwargs['fname'] = None
        super().__init__(*args, **kwargs)

    def load_module(self, fqname, fp, pathname, file_info):
        if not (fqname.startswith(self.package.__name__) or fqname == '__main__'):
            logger.debug('Skip finding {}'.format(fqname))
            return None
        return super().load_module(fqname, fp, pathname, file_info)


class ImportPath:
    """
    A direct dependency path between two modules. For example,
    if foo imports bar.baz, then the ImportPath is:
        ImportPath(
            importer='foo',
            imported='bar.baz'
        )
    """
    def __init__(self, importer, imported):
        """
        Args:
            importer (str): Absolute name of importing module.
            imported (str): Absolute name of module imported by importer.
        """
        self.importer = importer
        self.imported = imported

    def __str__(self):
        return "{} <- {}".format(self.importer, self.imported)

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self)


class IllegalModuleName(Exception):
    pass


class DependencyGraph:
    def __init__(self, package):
        self.package = package
        self.package_name = package.__name__
        sources = self._generate_pydep_sources()

        # The module count is the number of modules present in the dummy module.
        self.module_count = len(sources['__main__'])

        self._build_networkx_graph_from_sources(sources)
        pass

    def _generate_pydep_sources(self):
        dummy_module_filename = self._create_dummy_module()
        path = sys.path[:]
        path.insert(0, os.path.dirname(dummy_module_filename))

        finder = InternalModuleFinder(package=self.package)
        finder.run_script(dummy_module_filename)

        # Remove dummy file
        os.unlink(dummy_module_filename)

        self._sources = finder._depgraph

        return self._sources

    def _create_dummy_module(self):
        """
        Create a temporary file that imports every module within the supplied python package.
         Return:
            The name of the dummy file (string).
        """
        dummy_module_filename = '_dummy_%s.py' % self.package.__name__
        # Below causes problems with external python packages
        package_directory = os.path.dirname(self.package.__file__)

        with open(dummy_module_filename, 'w') as dummy_file:
            for module_filename in self._get_python_files_inside_package(package_directory):
                try:
                    module_name = self._module_name_from_filename(module_filename,
                                                                  package_directory)
                except IllegalModuleName:
                    logger.debug('Skipped illegal module {}.'.format(module_filename))
                    continue
                self._write_import_to_file(dummy_file, module_name)

        return dummy_module_filename

    def _get_python_files_inside_package(self, directory):
        """
        Get a list of Python files within the supplied package directory.
         Return:
            Generator of Python file names.
        """
        for root, dirs, files in os.walk(directory):
            # Don't include directories that aren't Python packages,
            # nor their subdirectories.
            if '__init__.py' not in files:
                [dirs.remove(d) for d in list(dirs)]
                continue
            # Don't include hidden directories.
            dotdirs = [d for d in dirs if d.startswith('.')]
            for d in dotdirs:
                dirs.remove(d)
            for filename in files:
                if is_python_file(filename):
                    yield os.path.abspath(os.path.join(root, filename))

    def _module_name_from_filename(self, filename_and_path, package_directory):
        """
        Args:
            filename_and_path (string) - the full name of the Python file.
            package_directory (string) - the full path of the top level Python package directory.
         Returns:
            Absolute module name for importing (string).
        """
        if not filename_and_path.startswith(package_directory):
            raise ValueError('Filename and path should be in the package directory.')  # pragma: no cover
        if not filename_and_path[-3:] == '.py':
            raise ValueError('Filename is not a Python file.')  # pragma: no cover
        container_directory, package_name = os.path.split(package_directory)
        internal_filename_and_path = filename_and_path[len(package_directory):]
        internal_filename_and_path_without_extension = internal_filename_and_path[1:-3]
        components = [package_name] + internal_filename_and_path_without_extension.split('/')
        if components[-1] == '__init__':
            components.pop()
        if any(map(iskeyword, components)):
            raise IllegalModuleName
        return '.'.join(components)

    def _write_import_to_file(self, fp, module):
        if 'migrations' in module:
            # This is used in Pydeps' original function, probably to remove noise when analysing
            # Django projects.
            logger.debug("Skipped printing {} to file because it looks like a migrations "
                         "file.".format(module))
            return
        print("try:", file=fp)
        print("    import", module, file=fp)
        print("except:", file=fp)
        print("    pass", file=fp)
        logger.debug('Wrote import to file: {}.'.format(module))

    def _build_networkx_graph_from_sources(self, sources):
        self._networkx_graph = networkx.DiGraph()
        self.dependency_count = 0
        for module_name, imported_modules in sources.items():
            if module_name == '__main__':
                #  Skip; this is just the dummy module.
                continue
            for upstream_module in imported_modules:
                if upstream_module.startswith(self.package_name):
                    self._add_path_to_networkx_graph(
                        ImportPath(
                            importer=module_name,
                            imported=upstream_module,
                        )
                    )
                    self.dependency_count += 1

    def find_path(self, downstream, upstream, ignore_paths=None):
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

    def _add_path_to_networkx_graph(self, import_path):
        self._networkx_graph.add_edge(import_path.importer, import_path.imported)

    def _remove_path_from_networkx_graph(self, import_path):
        self._networkx_graph.remove_edge(import_path.importer, import_path.imported)

    def _import_path_is_in_networkx_graph(self, import_path):
        return self._networkx_graph.has_successor(
            import_path.importer, import_path.imported
        )

    def _remove_paths_from_networkx_graph(self, import_paths):
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

    def _restore_paths_to_networkx_graph(self, import_paths):
        for import_path in import_paths:
            self._add_path_to_networkx_graph(import_path)

