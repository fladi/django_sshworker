#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import io
import re
from glob import glob
from os.path import (
    basename,
    dirname,
    join,
    splitext,
)

from setuptools import (
    find_packages,
    setup,
)


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='django-sshworker',
    license='BSD',
    description='SSH workers for Django',
    long_description=re.compile(
        '^.. start-badges.*^.. end-badges',
        re.M | re.S
    ).sub(
        '',
        read('README.rst')
    ),
    author='Michael Fladischer',
    author_email='michael.fladischer@medunigraz.at',
    url='https://github.com/fladi/django-sshworker',
    use_scm_version=True,
    setup_requires=[
        'setuptools_scm',
    ],
    install_requires=[
        'Django',
        'asyncssh',
    ],
    packages=find_packages(
        where='src',
        include=[
            'django_sshworker',
            'django_sshworker.*',
        ]
    ),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
    keywords=[
        'ssh',
        'worker',
        'process',
    ]
)
