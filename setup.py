from setuptools import find_packages, setup
import sys
import ast
import re
import os

_version_re = re.compile(r'VERSION\s+=\s+(.*)')

with open('graphene_django_extras/__init__.py', 'rb') as f:
    version = ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1))    
    version = ".".join([str(v) for v in version])

def get_packages():
    return [dirpath
            for dirpath, dirnames, filenames in os.walk('graphene_django_extras')
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]

setup(
    name='graphene-django-extras',
    version=version,

    description='Graphene-Django-Extras add some extra funcionalities to graphene-django to facilitate the graphql use without Relay and allow pagination and filtering integration',
    long_description=open('README.rst').read(),

    url='https://github.com/eamigo86/graphene-django-extras',

    author='Ernesto Perez Amigo',
    author_email='eamigo@nauta.cu',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    keywords='api graphql protocol rest graphene django',

    packages=get_packages(),

    install_requires=[        
        'graphene-django>=2.0.dev',
        'Django>=1.8.0',
        'django-filter', 
        'djangorestframework>=3.6.3',       
    ],    
    include_package_data=True,
    zip_safe=False,
    platforms='any',
)
