from typing import List, Iterator
import os
import logging

from keyword import iskeyword

from ..module import SafeFilenameModule


logger = logging.getLogger(__name__)


class IllegalModuleName(Exception):
    pass


class PackageScanner:
    def __init__(self, package: SafeFilenameModule) -> None:
        self.package = package

    def scan_for_modules(self) -> List[SafeFilenameModule]:
        """
        Returns:
            List of module names (list(str, ...)).

        Sets illegal_module_filenames as an attribute, that can be accessed to see if there were
        any modules that couldn't be imported due to their filenames being invalid.
        """
        package_directory = os.path.dirname(self.package.filename)
        modules: List[SafeFilenameModule] = []
        self.illegal_module_filenames: List[str] = []

        for module_filename in self._get_python_files_inside_package(package_directory):
            try:
                module_name = self._module_name_from_filename(module_filename,
                                                              package_directory)
                modules.append(
                    SafeFilenameModule(module_name, module_filename)
                )
            except IllegalModuleName:
                self.illegal_module_filenames.append(module_filename)
                logger.debug('Skipped illegal module {}.'.format(module_filename))
                continue

        # TODO raise NoModulesFound?
        return modules

    def _get_python_files_inside_package(self, directory: str) -> Iterator[str]:
        """
        Get a list of Python files within the supplied package directory.
         Return:
            Generator of Python file names.
        """
        for root, dirs, files in os.walk(directory):
            # Don't include directories that aren't Python packages,
            # nor their subdirectories.
            if '__init__.py' not in files:
                for d in list(dirs):
                    dirs.remove(d)
                continue

            # Don't include hidden directories.
            dirs_to_remove = [d for d in dirs if self._should_ignore_dir(d)]
            for d in dirs_to_remove:
                dirs.remove(d)

            for filename in files:
                if self._is_python_file(filename):
                    yield os.path.join(root, filename)

    def _should_ignore_dir(self, directory: str) -> bool:
        # TODO: make this configurable.
        # Skip adding directories that are hidden, or look like Django migrations.
        return directory.startswith('.') or directory == 'migrations'

    def _is_python_file(self, filename: str) -> bool:
        """
        Given a filename, return whether it's a Python file.

        Args:
            filename (str): the filename, excluding the path.
        Returns:
            bool: whether it's a Python file.
        """
        return not filename.startswith('.') and filename.endswith('.py')

    def _module_name_from_filename(self, filename_and_path: str, package_directory: str) -> str:
        """
        Args:
            filename_and_path (string) - the full name of the Python file.
            package_directory (string) - the full path of the top level Python package directory.
         Returns:
            Absolute module name for importing (string).
        """
        if not filename_and_path.startswith(package_directory):
            raise ValueError('Filename and path should be in the package directory.')
        if not filename_and_path[-3:] == '.py':
            raise ValueError('Filename is not a Python file.')
        container_directory, package_name = os.path.split(package_directory)
        internal_filename_and_path = filename_and_path[len(package_directory):]
        internal_filename_and_path_without_extension = internal_filename_and_path[1:-3]
        components = [package_name] + internal_filename_and_path_without_extension.split('/')
        if components[-1] == '__init__':
            components.pop()
        contains_keyword = any(map(iskeyword, components))
        is_valid_identifier = all([c.isidentifier() for c in components])
        if contains_keyword or not is_valid_identifier:
            raise IllegalModuleName
        return '.'.join(components)