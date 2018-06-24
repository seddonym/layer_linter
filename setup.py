#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'networkx>=2.1,<3',
    'pydeps>=1.5.1,<2',
    'PyYAML>=3.12,<4',
]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="David Seddon",
    author_email='david@seddonym.me',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Layer Linter checks that your project follows a custom-defined layered architecture.",
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='layer_linter',
    name='layer_linter',
    packages=find_packages(include=['layer_linter']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/seddonym/layer_linter',
    version='0.2.0',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'layer-lint = layer_linter.cmdline:main',
        ],
    },
)
