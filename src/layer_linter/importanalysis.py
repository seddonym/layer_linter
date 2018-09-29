from typing import List, Dict
import logging

from .module import SafeFilenameModule, Module
from .dependencies.graph import DependencyGraph
from .cmdline.layer_lint import _get_package


logger = logging.getLogger(__name__)


class ImportAnalysis:
    def __init__(self, module: Module) -> None:
        self.module = module
        self.imported_modules = self._find_imported_modules()

    def _find_imported_modules(self) -> Dict[Module, List[Module]]:
        package = self._package_from_module(self.module)
        graph = DependencyGraph(package)
        modules_to_check = [self.module] + graph.get_descendants(self.module)
        imported_modules = {}
        for importing_module in modules_to_check:
            for imported_module in graph.get_modules_directly_imported_by(importing_module):
                if imported_module.name.startswith(self.module.name):
                    continue
                if imported_module not in imported_modules:
                    imported_modules[imported_module] = []
                imported_modules[imported_module].append(importing_module)

        return imported_modules

    def _package_from_module(self, module: Module) -> SafeFilenameModule:
        """
        Get the root package, given a module.

        # TODO relocate _get_package.
        """
        package_name = module.name.split('.')[0]
        return _get_package(package_name)
