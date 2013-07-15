#!/usr/bin/env python
from setuptools import setup

setup(
    name='Certificator',
    version='0.1.0',
    long_description=__doc__,
    packages=['certificator'],
    include_package_data=True,
    zip_safe=False,
    setup_requires=[
        'nose>=1.0'
        ],
    tests_require=[
        'nose>=1.2.1',
        'coverage==3.6',
        'Flask-Testing==0.4',
        ],
    install_requires=[
        'Flask==0.9',
        'Flask-SQLAlchemy==0.16',
        'Flask-Script==0.5.3',
        'Jinja2==2.6',
        'SQLAlchemy==0.8.1',
        'Werkzeug==0.8.3',
        'twill==0.9',
        'wsgiref==0.1.2',
        ],
    entry_points={
        'console_scripts': [
            'certificator-server = certificator.main:main',
            ],
        }
)
