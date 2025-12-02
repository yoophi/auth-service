#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    "Click>=8.0",
    "Flask>=3.0,<4.0",
    "authlib>=1.0,<2.0",
    "email-validator>=2.0",
    "Flask-Migrate>=4.0",
    "Flask-Cors>=6.0",
    "Flask-Login>=0.6",
    "Flask-Marshmallow>=1.0",
    "Flask-SQLAlchemy>=3.0",
    "Flask-Swagger>=0.2.14",
    "google-api-core>=2.0,<3.0",
    "requests>=2.28",
    "psycopg2-binary>=2.9",
    "flask-social-login>=0.2.2",
]

setup_requirements = ['pytest-runner>=6.0', ]

test_requirements = ['pytest>=8.0', ]

setup(
    author="Pyunghyuk Yoo",
    author_email='yoophi@gmail.com',
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
    ],
    description="Python Boilerplate contains all the boilerplate you need to create a Python package.",
    entry_points={
        'console_scripts': [
            'auth_service=auth_service.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='auth_service',
    name='auth_service',
    packages=find_packages(include=['auth_service', 'auth_service.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/yoophi/auth_service',
    version='0.1.0',
    zip_safe=False,
)
