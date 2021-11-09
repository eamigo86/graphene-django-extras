#!/usr/bin/env python

import sys

import os
from os.path import dirname
from setuptools import find_packages, setup

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
BASE_PKG_DIR = BASE_DIR

if os.path.exists(BASE_PKG_DIR) and os.path.isdir(BASE_PKG_DIR):
    sys.path.insert(0, BASE_PKG_DIR)
else:
    raise ValueError('Error in path')


def get_file_contents(filename):
    with open(os.path.join(dirname(__file__), filename)) as fp:
        return fp.read()


def get_install_requires():
    requirements = get_file_contents('requirements.txt')
    install_requires = []
    for line in requirements.split('\n'):
        line = line.strip()
        if line and not line.startswith('-'):
            install_requires.append(line)
    return install_requires


setup(
        name='quartic_graphene_django_extras',
        description='Extra helper plugins for Graphene',
        author='Quartic.ai Engineering Team',
        long_description=get_file_contents('README.md'),
        author_email='tech@quartic.ai',
        url='https://github.com/eamigo86/graphene-django-extras/',
        classifiers=[
            'Programming Language :: Python :: 3.9'
        ],
        install_requires=get_install_requires(),
        include_package_data=True,
        keywords='deming core',
        packages=find_packages(exclude=['tests*']),
        package_data={
            # If any package contains *.so or *.pyi or *.lic files or *.key files,
            # include them:
            "": ["*.so", "*.pyi", "*.lic", "*.key"],
        },
)
