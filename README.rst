ExtractCode
===========

- license: Apache-2.0
- copyright: copyright (c) nexB. Inc. and others
- homepage_url: https://github.com/nexB/extractode
- keywords: archive, extraction, libarchive, 7zip, scancode-toolkit


ExtractCode is a universal archive extractor. It uses behind the scenes 
the Python standard library, a custom ctypes binding to libarchive and
the 7zip command line to extract a large number of common and
less common archives and compressed files. It tries to extract things
in the same way on all OSes, including auto-renaming files that would
not have valid names on certain filesystems or when there are multiple
copies of the same path in a given archive.
The extraction is driven from  a "voting" system that considers the
file extension(s) and name, the file type and mime type (using a ctypes
binding to libmagic) to select the most appropriate extractor or
uncompressor function. It can handle multi-level archives such as tar.gz.



Visit https://aboutcode.org and https://github.com/nexB/ for support and download.

To set up the development environment::

    source configure

To run unit tests::

    pytest -vvs -n 2

To clean up development environment::

    ./configure --clean


