from typing import Any

from ..module import Module


class ImportPath:
    """
    A direct dependency path between two modules. For example,
    if foo imports bar.baz, then the ImportPath is:
        ImportPath(
            importer=Module('foo'),
            imported=Module('bar.baz'),
        )
    """
    def __init__(self, importer: Module, imported: Module) -> None:
        self.importer = importer
        self.imported = imported

    def __str__(self) -> str:
        return "{} <- {}".format(self.importer, self.imported)

    def __repr__(self) -> str:
        return '<{}: {}>'.format(self.__class__.__name__, self)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ImportPath):
            return (self.importer, self.imported) == (other.importer, other.imported)
        else:
            return False

    def __hash__(self) -> int:
        return hash(str(self))
