ExtractCode
===========

CommonCode
==========

- license: Apache-2.0
- copyright: copyright (c) nexB. Inc. and others
- homepage_url: https://github.com/nexB/extractode
- keywords: archiev, extraction, libarchive, 7zip, scancode-toolkit

A set of functions and utilities used to extract archives in a mostly universal way.
This libraries uses multiple techniques to extract archives reliably including
using the Python standard library, and bundled 7zip and libarchive to use the
best tool to extract evebtually any archive and compressed file.


Visit https://aboutcode.org and https://github.com/nexB/ for support and download.

To set up the development environment::

    source configure

To run unit tests::

    pytest -vvs -n 2

To clean up development environment::

    ./configure --clean


