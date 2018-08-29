from typing import Any


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

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return "<{}: {}>".format(self.__class__.__name__, self)

    def __eq__(self, other: Any) -> bool:
        # Only other Module instances with the same name are equal to each other.
        if isinstance(other, Module):
            return self.name == other.name
        else:
            return False

    def __hash__(self) -> int:
        return hash(str(self))


class SafeFilenameModule(Module):
    """
    A Python module whose filename can be known safely, without importing the code.
    """
    def __init__(self, name: str, filename: str) -> None:
        """
        Args:
            name: The fully qualified name of a Python module, e.g. 'package.foo.bar'.
            filename: The full filename and path to the Python file,
            e.g. '/path/to/package/one.py'.
        """
        self.filename = filename
        super().__init__(name)
