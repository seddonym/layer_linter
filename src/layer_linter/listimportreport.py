from typing import List

from .importanalysis import ImportAnalysis
from .module import Module
from .report import ConsolePrinter  # TODO move into separate module.


class ImportsReport:
    def __init__(self, analysis: ImportAnalysis) -> None:
        self.analysis = analysis

    def output(self) -> None:
        ConsolePrinter.print_heading(f'Modules imported by {self.analysis.module}',
                                     ConsolePrinter.HEADING_LEVEL_TWO)
        for imported_module, importing_modules in self.analysis.imported_modules.items():
            self._output_imported_module(imported_module, importing_modules)

    def _output_imported_module(self,
                                imported_module: Module,
                                importing_modules: List[Module]) -> None:
        ConsolePrinter.indent_cursor()
        importers = ', '.join([str(m) for m in importing_modules])
        ConsolePrinter.print(f'- {imported_module} (imported by {importers})')
