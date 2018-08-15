import sys
import os
import logging
from collections import defaultdict
from modulefinder import ModuleFinder

from .path import ImportPath


logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """
    Analyzes a set of Python modules for imports between them.

    Args:
        modules: list of module names (list(str, ...)).
        package: Python package that contains all the modules (module).
    Usage:

        analyzer = DependencyAnalyzer(modules)
        import_paths = analyzer.determine_import_paths()
    """
    def __init__(self, modules, package):
        self.modules = modules
        self.package = package
        self.current = 0
        self.high = 10

    def determine_import_paths(self):
        sources = self._find_import_sources()
        return self._sources_to_import_paths(sources)

    def _find_import_sources(self):
        dummy_module_filename = self._create_dummy_module()
        path = sys.path[:]
        path.insert(0, os.path.dirname(dummy_module_filename))

        finder = _InternalModuleFinder(package=self.package)
        finder.run_script(dummy_module_filename)

        # Remove dummy file
        os.unlink(dummy_module_filename)

        self._sources = finder.dependencies

        return self._sources

    def _create_dummy_module(self):
        """
        Create a temporary file that imports every module within the supplied python package.
         Return:
            The name of the dummy file (string).
        """
        dummy_module_filename = '_dummy_%s.py' % self.package.__name__

        with open(dummy_module_filename, 'w') as dummy_file:
            for module_name in self.modules:
                self._write_import_to_file(dummy_file, module_name)

        return dummy_module_filename

    def _write_import_to_file(self, fp, module):
        print("try:", file=fp)
        print("    import", module, file=fp)
        print("except:", file=fp)
        print("    pass", file=fp)
        logger.debug('Wrote import to file: {}.'.format(module))

    def _sources_to_import_paths(self, sources):
        import_paths = []
        for importer, imported_list in sources.items():
            if importer != '__main__':
                for imported in imported_list:
                    import_paths.append(
                        ImportPath(importer=importer, imported=imported)
                    )
        return import_paths


class _InternalModuleFinder(ModuleFinder):
    """
    Analyses the internal dependencies for a Python package.

    The ModuleFinder API is a bit unintuitive. You instantiate the module finder with the Python
    package that you want to analyse:

         package = __import__('mypackage')
         finder = _InternalModuleFinder(package)

    Then you pass `run_script` the name of a Python module, built elsewhere, that contains imports
    of all the modules within that package:

         finder.run_script('path/to/dummy_module.py')

    Finally you can access a dictionary containing all the import information for each imported
    module:
         dependencies = finder.dependencies

    Credits:
        This method of analysing dependencies on a Python project is inspired by the
        pydeps project (https://github.com/thebjorn/pydeps).
    """
    def __init__(self, *args, package, **kwargs):
        self.package = package
        self.dependencies = defaultdict(list)
        self._last_caller = None
        super().__init__(*args, **kwargs)

    def load_module(self, fqname, fp, pathname, file_info):
        if not (fqname.startswith(self.package.__name__) or fqname == '__main__'):
            # Only analyse dependencies belonging to the package.
            return None
        return super().load_module(fqname, fp, pathname, file_info)

    def import_hook(self, name, caller=None, fromlist=None, level=-1):
        # Store the last caller, so we can use it in _add_import_to_dependencies.
        old_last_caller = self._last_caller
        try:
            self._last_caller = caller
            super().import_hook(name, caller, fromlist, level)
        finally:
            self._last_caller = old_last_caller

    def import_module(self, partnam, fqname, parent):
        module = super().import_module(partnam, fqname, parent)
        self._add_import_to_dependencies(module)
        return module

    def ensure_fromlist(self, module, fromlist, recursive=0):
        super().ensure_fromlist(module, fromlist, recursive)
        for sub in fromlist:
            if sub != "*" and hasattr(module, sub):
                self._add_import_to_dependencies(getattr(module, sub))

    def _add_import_to_dependencies(self, module):
        """
        Add a module to the dependency graph.

        Args:
            module (Module): the module to add.

        This method relies on ModuleFinder recursive drilling down of imports. In import_hook,
        we set the last caller so we know what module imported this one.
        """
        if module is not None:
            if self._last_caller:
                importer_module_name = self._last_caller.__name__
                trimmed_list = []
                for imported_module_name in self.dependencies[importer_module_name]:
                    if not module.__name__.startswith(imported_module_name):
                        trimmed_list.append(imported_module_name)
                self.dependencies[importer_module_name] = trimmed_list + [module.__name__]

    def scan_code(self, co, m):
        """
        Given some bytecode from a module, recursively import modules imported by the bytecode.

        Args:
            co (code): some bytecode from a module.
            m (Module): the module that contains the bytecode.
        This is copied from ModuleFinder.scan_code, with a few edits (see comments).
        """
        code = co.co_code
        # LAYER LINTER EDIT.
        try:
            # Python >= 3.6.
            scanner = self.scan_opcodes
        except AttributeError:
            # Python < 3.6.
            scanner = self.scan_opcodes_25
        # END LAYER LINTER EDIT.
        for what, args in scanner(co):
            if what == "store":
                name, = args
                m.globalnames[name] = 1
            elif what == "absolute_import":
                fromlist, name = args
                have_star = 0
                if fromlist is not None:
                    if "*" in fromlist:
                        have_star = 1
                    fromlist = [f for f in fromlist if f != "*"]
                self._safe_import_hook(name, m, fromlist, level=0)
                if have_star:
                    # We've encountered an "import *". If it is a Python module,
                    # the code has already been parsed and we can suck out the
                    # global names.
                    mm = None
                    if m.__path__:
                        # At this point we don't know whether 'name' is a
                        # submodule of 'm' or a global module. Let's just try
                        # the full name first.
                        mm = self.modules.get(m.__name__ + "." + name)
                    if mm is None:
                        mm = self.modules.get(name)
                    if mm is not None:
                        m.globalnames.update(mm.globalnames)
                        m.starimports.update(mm.starimports)
                        if mm.__code__ is None:
                            m.starimports[name] = 1
                    else:
                        m.starimports[name] = 1
            elif what == "relative_import":
                level, fromlist, name = args
                if name:
                    self._safe_import_hook(name, m, fromlist, level=level)
                else:
                    parent = self.determine_parent(m, level=level)
                    # LAYER LINTER EDIT.
                    # The original doesn't pass the module to safe_import_hook
                    # (seems like a bug?)
                    self._safe_import_hook(parent.__name__, m, fromlist, level=0)
                    # END LAYER LINTER EDIT.
            else:
                # We don't expect anything else from the generator.
                raise RuntimeError(what)

        for c in co.co_consts:
            if isinstance(c, type(co)):
                self.scan_code(c, m)
