#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'networkx~=2.2',
    'PyYAML~=4.2b1',
    'click>=6.7,<8',
]

setup(
    author="David Seddon",
    author_email='david@seddonym.me',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Layer Linter checks that your project follows a custom-defined layered architecture.",
    install_requires=requirements,
    license="BSD license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='layer-linter layer-lint',
    name='layer-linter',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    url='https://github.com/seddonym/layer_linter',
    version='0.12.2',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'layer-lint = layer_linter.cmdline:main',
        ],
    },
)
