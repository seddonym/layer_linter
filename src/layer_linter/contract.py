from typing import List, Dict, Iterable, Optional
import re
import yaml
import importlib
import logging
from copy import copy

from .dependencies import DependencyGraph, ImportPath
from .module import Module


logger = logging.getLogger(__name__)


class ContractParseError(IOError):
    pass


class Layer:
    """
    A relatively named module or subpackage. When combined with a container,
    it refers to a specific module. For example, Layer('one') would refer
    to Module('foo.one') when combined with the containing Module('foo').

    If a Layer is marked as optional, then a Contract won't complain if
    it can't find it within a particular container.
    """
    def __init__(self, name: str, is_optional=False) -> None:
        self.name = name
        self.is_optional = is_optional

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return '<{}: {}>'.format(self.__class__.__name__, self)


class Contract:
    def __init__(self, name: str, containers: List[Module], layers: List[Layer],
                 whitelisted_paths: Optional[List[ImportPath]] = None) -> None:
        self.name = name
        self.containers = containers
        self.layers = layers
        self.whitelisted_paths = whitelisted_paths if whitelisted_paths else []

    def check_dependencies(self, dependencies: DependencyGraph) -> None:
        self._check_all_layers_exist_for_all_containers(dependencies)

        self.illegal_dependencies: List[List[str]] = []

        logger.debug('Checking dependencies for contract {}...'.format(self))

        for container in self.containers:
            for layer in reversed(self.layers):
                self._check_layer_does_not_import_downstream(layer, container, dependencies)

    def _check_all_layers_exist_for_all_containers(self, dependencies: DependencyGraph) -> None:
        """
        Raise a ValueError if we couldn't find any Python files for each layer in all containers.
        """
        for container in self.containers:
            self._check_all_layers_exist_for_container(container, dependencies)

    def _check_all_layers_exist_for_container(self,
                                              container: Module,
                                              dependencies: DependencyGraph) -> None:
        """
        Raise a ValueError if we couldn't find any Python files for each non-optional layer.
        """
        for layer in self.layers:
            if layer.is_optional:
                continue
            layer_module = self._get_layer_module(layer, container)
            if layer_module not in dependencies:
                raise ValueError(f"Missing layer in container '{container}': "
                                 f"module {layer_module} does not exist.")

    def _check_layer_does_not_import_downstream(self, layer: Layer, container: Module,
                                                dependencies: DependencyGraph) -> None:

        logger.debug("Layer '{}' in container '{}'.".format(layer, container))

        modules_in_this_layer = self._get_modules_in_layer(layer, container, dependencies)
        modules_in_downstream_layers = self._get_modules_in_downstream_layers(
            layer, container, dependencies)
        logger.debug('Modules in this layer: {}'.format(modules_in_this_layer))
        logger.debug('Modules in downstream layer: {}'.format(modules_in_downstream_layers))

        for upstream_module in modules_in_this_layer:
            for downstream_module in modules_in_downstream_layers:
                logger.debug('Upstream {}, downstream {}.'.format(upstream_module,
                                                                  downstream_module))
                path = dependencies.find_path(
                    upstream=downstream_module,
                    downstream=upstream_module,
                    ignore_paths=self.whitelisted_paths,
                )
                logger.debug('Path is {}.'.format(path))
                if path and not self._path_is_via_another_layer(path, layer, container):
                    logger.debug('Illegal dependency found: {}'.format(path))
                    self._update_illegal_dependencies(path)

    def _get_modules_in_layer(
        self, layer: Layer, container: Module, dependencies: DependencyGraph
    ) -> List[Module]:
        """
        Args:
            layer: The Layer object.
            container: absolute name of the package containing the layer (string).
            dependencies: the DependencyGraph object.
        Returns:
            List of modules names within that layer, including the layer module itself.
            Includes grandchildren and deeper.
        """
        layer_module = self._get_layer_module(layer, container)
        modules = [layer_module]
        modules.extend(
            dependencies.get_descendants(layer_module)
        )
        return modules

    def _get_layer_module(self, layer: Layer, container: Module) -> Module:
        return Module("{}.{}".format(container, layer.name))

    def _get_modules_in_downstream_layers(
        self, layer: Layer, container: Module, dependencies: DependencyGraph
    ) -> List[Module]:
        modules = []
        for downstream_layer in self._get_layers_downstream_of(layer):
            modules.extend(
                self._get_modules_in_layer(layer=downstream_layer, container=container,
                                           dependencies=dependencies)
            )
        return modules

    def _path_is_via_another_layer(self, path, current_layer, container):
        other_layers = list(copy(self.layers))
        other_layers.remove(current_layer)

        layer_modules = ['{}.{}'.format(container, layer.name) for layer in other_layers]
        modules_via = path[1:-1]

        return any(path_module in layer_modules for path_module in modules_via)

    def _update_illegal_dependencies(self, path):
        # Don't duplicate path. So if the path is already present in another dependency,
        # don't add it. If another dependency is present in this path, replace it with this one.
        new_path_set = set(path)
        logger.debug('Updating illegal dependencies with {}.'.format(path))
        illegal_dependencies_copy = self.illegal_dependencies[:]
        paths_to_remove = []
        add_path = True
        for existing_path in illegal_dependencies_copy:
            existing_path_set = set(existing_path)
            logger.debug('Comparing new path with {}...'.format(existing_path))
            if new_path_set.issubset(existing_path_set):
                # Remove the existing_path, as the new path will be more succinct.
                logger.debug('Removing existing.')
                paths_to_remove.append(existing_path)
                add_path = True
            elif existing_path_set.issubset(new_path_set):
                # Don't add the new path, it's implied more succinctly with the existing path.
                logger.debug('Skipping new path.')
                add_path = False

        logger.debug('Paths to remove: {}'.format(paths_to_remove))
        self.illegal_dependencies = [
            i for i in self.illegal_dependencies if i not in paths_to_remove
        ]
        if add_path:
            self.illegal_dependencies.append(path)

    @property
    def is_kept(self) -> bool:
        try:
            return len(self.illegal_dependencies) == 0
        except AttributeError:
            raise RuntimeError(
                'Cannot check whether contract is kept '
                'until check_dependencies is called.'
            )

    def _get_layers_downstream_of(self, layer: Layer) -> Iterable[Layer]:
        return reversed(self.layers[:self.layers.index(layer)])

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return '<{}: {}>'.format(self.__class__.__name__, self)


PARENTHESES_REGEX = re.compile(r'^\(.*\)$')


def contract_from_yaml(key: str, data: Dict, package_name: str) -> Contract:
    layers: List[Layer] = []
    if 'layers' not in data:
        raise ContractParseError(f"'{key}' is missing a list of layers.")
    for layer_name in data['layers']:
        if PARENTHESES_REGEX.match(layer_name):
            layer = Layer(layer_name[1:-1], is_optional=True)
        else:
            layer = Layer(layer_name)
        layers.append(layer)

    containers: List[Module] = []
    if 'containers' not in data:
        error_message = f"'{key}' is missing a list of containers."
        # Help users who are using the older format.
        if 'packages' in data:
            error_message += " (Tip: try renaming 'packages' to 'containers'.)"
        raise ContractParseError(error_message)

    for container_name in data['containers']:
        _validate_container_name(container_name, package_name)
        containers.append(Module(container_name))

    whitelisted_paths: List[ImportPath] = []
    for whitelist_data in data.get('whitelisted_paths', []):
        try:
            importer, imported = map(Module, whitelist_data.split(' <- '))
        except ValueError:
            raise ValueError('Whitelisted paths must be in the format '
                             '"importer.module <- imported.module".')

        whitelisted_paths.append(ImportPath(importer, imported))

    return Contract(
        name=key,
        containers=containers,
        layers=layers,
        whitelisted_paths=whitelisted_paths,
    )


def get_contracts(filename: str, package_name: str) -> List[Contract]:
    """Read in any contracts from the given filename.
    """
    contracts = []

    with open(filename, 'r') as file:
        try:
            data_from_yaml = yaml.load(file)
        except Exception as e:
            logger.debug(e)
            raise ContractParseError('Could not parse {}.'.format(filename))
        for key, data in data_from_yaml.items():
            contracts.append(contract_from_yaml(key, data, package_name))

    return contracts


def _validate_container_name(container_name, package_name):
    """Raise a ValueError if the suppled container name is not a valid container for the supplied
    package name.
    """
    if not container_name.startswith(package_name):
        raise ValueError(
            f"Invalid container '{container_name}': containers must be either a "
            f"subpackage of '{package_name}', or '{package_name}' itself."
        )

    # Check that the container actually exists.
    if importlib.util.find_spec(container_name) is None:
        raise ValueError(
            f"Invalid container '{container_name}': no such package."
        )
