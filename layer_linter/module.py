from typing import Any
from importlib.util import find_spec


class Module:
    """
    A Python module.
    """
    def __init__(self, name: str) -> None:
        """
        Args:
            name: The fully qualified name of a Python module, e.g. 'package.foo.bar'.
        """
        self.name = name
        self._filename: str = None

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return "<{}: {}>".format(self.__class__.__name__, self)

    def __eq__(self, other: Any) -> bool:
        return str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))

    def store_filename(self, filename: str):
        self._filename = filename

    def get_filename(self) -> str:
        # This, combined with store_filename, is a bit of a smell. It's useful to be able to
        # instantiate Module objects without needing the file path (e.g. in contracts),
        # but the analyzer needs to know the file path *without* loading the module. We actually
        # know the filepath when creating the module ahead of time in the scanner, so we can store
        # it then, ready for the analyzer. Probably the best approach would be to use a different
        # type (maybe a subclass of Module) for the analyzer / scanner relationship, which
        # requires the file as well as the name when instantiating. The alternative is to write
        # something here which works out what the module file is from the name.
        if not self._filename:
            spec = find_spec(self.name)
            self._filename = spec.origin  # type: ignore
        return self._filename
