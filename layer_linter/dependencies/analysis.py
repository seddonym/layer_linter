from typing import List
import ast

import logging

from ..module import Module, SafeFilenameModule
from .path import ImportPath


logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """
    Analyzes a set of Python modules for imports between them.

    Args:
        modules: list of all SafeFilenameModules that make up the package.
        package: tmylpyhe Python package that contains all the modules.
    Usage:

        analyzer = DependencyAnalyzer(modules)
        import_paths = analyzer.determine_import_paths()
    """
    def __init__(self, modules: List[SafeFilenameModule], package: Module) -> None:
        self.modules = modules
        self.package = package

    def determine_import_paths(self) -> List[ImportPath]:
        import_paths: List[ImportPath] = []
        for module in self.modules:
            import_paths.extend(
                self._get_import_paths(module)
            )
        return import_paths

    def _get_import_paths(self, module: SafeFilenameModule) -> List[ImportPath]:
        import_paths: List[ImportPath] = []
        imported_modules = self._get_imported_modules(module)
        for imported_module in imported_modules:
            import_paths.append(
                ImportPath(
                    importer=module,
                    imported=imported_module
                )
            )
        return import_paths

    def _get_imported_modules(self, module: SafeFilenameModule) -> List[Module]:
        """
        Statically analyses the given module and returns a list of Modules that it imports.

        Note: this method only analyses the module in question and will not load any other code,
        so it relies on self.modules to deduce which modules it imports. (This is because you
        can't know whether "from foo.bar import baz" is importing a module called `baz`,
        or a function `baz` from the module `bar`.)
        """
        imported_modules = []

        with open(module.filename) as file:
            module_contents = file.read()

        ast_tree = ast.parse(module_contents)
        for node in ast.walk(ast_tree):
            if isinstance(node, ast.ImportFrom):
                assert isinstance(node.level, int)
                if node.level == 0:
                    # Absolute import.
                    # Let the type checker know we expect node.module to be set here.
                    assert isinstance(node.module, str)
                    if not node.module.startswith(self.package.name):
                        # Don't include imports of modules outside this package.
                        continue
                    for alias in node.names:
                        full_module_name = '.'.join([node.module, alias.name])
                        imported_modules.append(Module(full_module_name))
                elif node.level >= 1:
                    # Relative import. The level corresponds to how high up the tree it goes;
                    # for example 'from ... import foo' would be level 3.
                    importing_module_components = module.name.split('.')
                    # TODO: handle level that is too high.
                    # Trim the base module by the number of levels.
                    module_base = '.'.join(importing_module_components[:-node.level])
                    if node.module:
                        module_base = '.'.join([module_base, node.module])
                    for alias in node.names:
                        full_module_name = '.'.join([module_base, alias.name])
                        imported_modules.append(Module(full_module_name))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if not alias.name.startswith(self.package.name):
                        # Don't include imports of modules outside this package.
                        continue
                    imported_modules.append(Module(alias.name))

        imported_modules = self._trim_each_to_known_modules(imported_modules)
        return imported_modules

    def _trim_each_to_known_modules(self, imported_modules: List[Module]) -> List[Module]:
        trimmed_modules = []
        for imported_module in imported_modules:
            if imported_module in self.modules:
                trimmed_modules.append(imported_module)
            else:
                # The module isn't in the known modules. This is because it's something *within*
                # a module (e.g. a function). So we trim the components back until we find
                # a module.
                components = imported_module.name.split('.')[:-1]
                found = False
                while components and not found:
                    candidate_module = Module('.'.join(components))
                    if candidate_module in self.modules:
                        trimmed_modules.append(candidate_module)
                        found = True
                        continue
                    components = components[:-1]
                # If we got here, we won't have found a candidate module.
        return trimmed_modules
