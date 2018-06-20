import argparse

from .cmdline import main


def create_parser():
    parser = argparse.ArgumentParser(
        description='Checks that your project follows a custom-defined '
        'layered architecture, based on a layers.yaml file.'
    )

    parser.add_argument(
        'package_name',
        help='The name of the Python package to validate.'
    )

    return parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    main(args.package_name)
