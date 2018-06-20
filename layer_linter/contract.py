import yaml
import os
import logging
from copy import copy


logger = logging.getLogger(__name__)


class Layer:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self)


class Contract:
    def __init__(self, name, packages, layers, recursive=False):
        self.name = name
        self.packages = packages
        self.layers = layers
        self.recursive = recursive

    def check_dependencies(self, dependencies):
        self.illegal_dependencies = []

        logger.debug('Checking dependencies for contract {}...'.format(self))

        for package in self.packages:
            for layer in self.layers:
                self._check_layer_does_not_import_downstream(layer, package, dependencies)

    def _check_layer_does_not_import_downstream(self, layer, package, dependencies):

        logger.debug("Layer '{}' in package '{}'.".format(layer, package))

        modules_in_this_layer = self._get_modules_in_layer(layer, package, dependencies)
        modules_in_downstream_layers = self._get_modules_in_downstream_layers(
            layer, package, dependencies)
        logger.debug('Modules in this layer: {}'.format(modules_in_this_layer))
        logger.debug('Modules in downstream layer: {}'.format(modules_in_downstream_layers))

        for upstream_module in modules_in_this_layer:
            for downstream_module in modules_in_downstream_layers:
                path = dependencies.find_path(
                    upstream=downstream_module,
                    downstream=upstream_module)
                if path and not self._path_is_via_another_layer(path, layer, package):
                    logger.debug('Illegal dependency found: {}'.format(path))
                    self.illegal_dependencies.append(path)

    def _get_modules_in_layer(self, layer, package, dependencies):
        """
        Args:
            layer: The Layer object.
            package: absolute name of the package containing the layer (string).
            dependencies: the DependencyGraph object.
        Returns:
            List of modules names within that layer, including the layer module itself.
            Includes grandchildren and deeper.
        """
        layer_module = "{}.{}".format(package, layer.name)
        modules = [layer_module]
        modules.extend(
            dependencies.get_descendants(layer_module)
        )
        return modules

    def _get_modules_in_downstream_layers(self, layer, package, dependencies):
        modules = []
        for downstream_layer in self._get_layers_downstream_of(layer):
            modules.extend(
                # self._get_modules_in_layer(downstream_layer, package, dependencies)
                ["{}.{}".format(package, downstream_layer.name)]
            )
        return modules

    def _path_is_via_another_layer(self, path, current_layer, package):
        other_layers = list(copy(self.layers))
        other_layers.remove(current_layer)

        layer_modules = ['{}.{}'.format(package, layer.name) for layer in other_layers]
        modules_via = path[1:-1]

        return any(path_module in layer_modules for path_module in modules_via)

    @property
    def is_kept(self):
        try:
            return len(self.illegal_dependencies) == 0
        except AttributeError:
            raise RuntimeError(
                'Cannot check whether contract is kept '
                'until check_dependencies is called.'
            )

    def _get_layers_downstream_of(self, layer):
        return self.layers[self.layers.index(layer) + 1:]

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self)


def contract_from_yaml(key, data):
    layers = []
    for layer_data in data['layers']:
        layers.append(Layer(layer_data))

    return Contract(
        name=key,
        packages=data['packages'],
        layers=layers,
    )


def get_contracts(path):
    """Given a path to a project, read in any contracts from a contract.yml file.
    Args:
        path (string): the path to the project root.
    Returns:
        A list of Contract instances.
    """
    contracts = []

    file_path = os.path.join(path, 'contracts.yml')

    with open(file_path, 'r') as file:
        data_from_yaml = yaml.load(file)
        for key, data in data_from_yaml.items():
            contracts.append(contract_from_yaml(key, data))

    return contracts
