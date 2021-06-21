==================
Outpost Django Geo
==================

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |requires|
        | |codecov|

.. |docs| image:: https://readthedocs.org/projects/outpost/badge/?style=flat
    :target: https://readthedocs.org/projects/outpost.django.geo
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/medunigraz/outpost.django.geo.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/medunigraz/outpost.django.geo

.. |requires| image:: https://requires.io/github/medunigraz/outpost.django.geo/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/medunigraz/outpost.django.geo/requirements/?branch=master

.. |codecov| image:: https://codecov.io/github/medunigraz/outpost.django.geo/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/medunigraz/outpost.django.geo

.. end-badges

Geographic data, positioning and in-house routing.

* Free software: BSD license

Documentation
=============

https://outpost.django.geo.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
