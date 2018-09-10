import ast
import os
import re

from setuptools import setup


_version_re = re.compile(r'VERSION\s+=\s+(.*)')
_name = 'graphene_django_extras'

with open('{}/__init__.py'.format(_name), 'rb') as f:
    version = ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1))
    version = ".".join([str(v) for v in version])
    version = version.split('.final')[0] if 'final' in version else version


def get_packages():
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(_name)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


setup(
    name=_name,
    version=version,

    description='graphene_django_extras add some extra funcionalities to graphene-django to facilitate '
                'the graphql use without Relay, allow paginations and filtering integration and add some'
                'extra directives',
    long_description=open('README.rst').read(),

    url='https://github.com/eamigo86/graphene-django-extras',

    author='Ernesto Perez Amigo',
    author_email='eamigo@nauta.cu',

    license='MIT',

    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    keywords='api graphql protocol rest graphene django',

    packages=get_packages(),

    install_requires=[
        'graphql-core>=2.0',
        'graphene>=2.0.1',
        'graphene-django>=2.0',
        'django-filter>=1.1.0',
        'djangorestframework>=3.6.0'
    ],
    extras_require={
        'date': [
            'python-dateutil>=2.7.3',
        ]
    },
    include_package_data=True,
    zip_safe=False,
    platforms='any',
)
