ExtractCode
===========

- license: Apache-2.0
- copyright: copyright (c) nexB. Inc. and others
- homepage_url: https://github.com/nexB/extractcode
- keywords: archive, extraction, libarchive, 7zip, scancode-toolkit, extractcode

Supports Windows, Linux and macOS on 64 bits processors and Python 3.6 to 3.9.


**ExtractCode is a (mostly) universal archive extractor.**

Install with::

    pip install extractcode[full]


Why another extractor?
----------------------

**it will extract!**

ExtractCode will extract things where other extractors may fail.

- Say you want to extract the tarball of the Linux kernel source code on Windows.
  It contains paths that are the same when ignoring the case and therefore will
  not extract OK on Windows: some file may be munged or the extract may file.

- Or a tarball (on any OS) may contain multiple times the exact same path. In
  these cases the paths showing up earlier in the archive may be "hidden" and
  overwritten by the same path showing up later in the archive giving the
  impression that there is only one file.

- Or an archive may be damaged a little but most files can still be extracted.

- Or the extracted files are such permissions that you cannot read them and are
  not owned by you.

- Or the archive may contain weird paths inluding relative paths that may be
  problematic to extract.

- Or the archive may contain special file types (character/device files) that
  may be problematic to extract.

- Or an archive may be a virtual disk or some file system(s) images that would
  typically need to be mounted to be accessed, and may require root access
  and guesswork to find out which partition and filesystem are at play and
  which driver to use.

In all these cases, ExtractCode will extract and try hard do the right thing to
obtain the actual archived content when other tools may fail.

It can also extract recursively any type of (nested) archives-in-archives

As a downside, the extracted content may not be exactly what would be expected
to use the contained files: for instance  ... but this it is perfectly OK for
file content analysis for software composition or forensic analysis.

Behind the scene, ExtractCode uses multiple tools such as:

- the Python standard library,
- a custom ctypes binding to libarchive,
- the 7zip command line tool, and
- optionally libguestfs on Linux.

With these, it is possible to extract a large number of common and less common
archives and compressed file types. ExtractCode tries to extract things in the
same way on all supported OSes, including auto-renaming files that would have
invalid, non-extractible names on certain filesystems or when there are multiple
copies of the same path in a given archive (which is possible in a tar).

The extraction is driven from  a "voting" system that considers the file
extension(s) and name, the filetype and mimetype (using a ctypes binding to
libmagic) to select the most appropriate extractor or decompressor function.
It can handle multi-level archives such as tar.gz and can extract recursively
any nested archives.

Visit https://aboutcode.org and https://github.com/nexB/ for support and download.


We run CI tests on:

 - Azure pipelines https://dev.azure.com/nexB/extractcode/_build


Installation
------------

To install this package with its full capability (where the binaries for
7zip and libarchive are installed), use the `full` extra option::

    pip install extractcode[full]

If you want to use the version of binaries (possibly) provided by your operating
system, use the `minimal` option::

    pip install extractcode

In this case, you will need to provide a working and compatible libarchive and
7zip installed and configured in one of these ways such that ExtractCode can
find them:

- **a typecode-libarchive and typecode-7z plugin**: See the standard ones at
  https://github.com/nexB/scancode-plugins/tree/main/builtins
  These can either bundle a libarchive library, a 7z executable or expose a
  system-installed libraries.
  It does so by providing plugin entry points as ``scancode_location_provider``
  for ``extractcode_libarchive`` that should point to a ``LocationProviderPlugin``
  subclass with a ``get_locations()`` method that must return a mapping with
  this key:

    - 'extractcode.libarchive.dll': the absolute path to a **libarchive** shared object/DLL

  See for example:

    - https://github.com/nexB/scancode-plugins/blob/4da5fe8a5ab1c87b9b4af9e54d7ad60e289747f5/builtins/extractcode_libarchive-linux/setup.py#L40
    - https://github.com/nexB/scancode-plugins/blob/4da5fe8a5ab1c87b9b4af9e54d7ad60e289747f5/builtins/extractcode_libarchive-linux/src/extractcode_libarchive/__init__.py#L17

  And in the same way, the ``scancode_location_provider`` for ``extractcode_7zip``
  should point to a ``LocationProviderPlugin`` subclass with a ``get_locations()``
  method that must return a mapping with this key:

    - 'extractcode.sevenzip.exe': the absolute path to a **7zip** executable

  See for example:

    - https://github.com/nexB/scancode-plugins/blob/4da5fe8a5ab1c87b9b4af9e54d7ad60e289747f5/builtins/extractcode_7z-linux/setup.py#L40
    - https://github.com/nexB/scancode-plugins/blob/4da5fe8a5ab1c87b9b4af9e54d7ad60e289747f5/builtins/extractcode_7z-linux/src/extractcode_7z/__init__.py#L18

- use **environment variables** to point to installed binaries:

    - EXTRACTCODE_LIBARCHIVE_PATH: the absolute path to a libarchive DLL
    - EXTRACTCODE_7Z_PATH: the absolute path to a 7zip executable


- **a system-installed libarchive and 7zip executable** available in the system **PATH**.


The supported binary tools versions are:

- libarchive  3.5.x
- 7zip 16.5.x


Development
-----------

To set up the development environment::

    source configure --dev


To run unit tests::

    pytest -vvs -n 2


To clean up development environment::

    ./configure --clean


To run the command line tool in the activated environment::

    ./extractcode -h


Configuration with environment variables
----------------------------------------

ExtractCode will use these environment variables if set:

- EXTRACTCODE_LIBARCHIVE_PATH : the path to the ``libarchive.so`` libarchive
  shared library used to support some of the archive formats. If not provided,
  ExtractCode will look for a plugin-provided libarchive library path. See
  https://github.com/nexB/scancode-plugins/tree/main/builtins for such plugins.
  If no plugin contributes libarchive, then a final attempt is made to look for
  it in the PATH using standard DLL loading techniques.

- EXTRACTCODE_7Z_PATH : the path to the ``7z`` 7zip executable used to support
  some of the archive formats. If not provided, ExtractCode will look for a
  plugin-provided 7z executable path. See
  https://github.com/nexB/scancode-plugins/tree/main/builtins for such plugins.
  If no plugin contributes 7z, then a final attempt is made to look for
  it in the PATH.

- EXTRACTCODE_GUESTFISH_PATH : the path to the ``guestfish`` tool from
  libguestfs to use to extract VM images. If not provided, ExtractCode will look
  in the PATH for an installed ``guestfish`` executable instead.



Adding support for VM images extraction
---------------------------------------

Adding support for VM images requires the manual installation of the
libguestfs-tools system package. This is suported only on Linux.
On Debian and Ubuntu you can use this command::

    sudo apt-get install libguestfs-tools


On Ubuntu only, an additional manual step is required as the kernel executable
file cannot be read by users as required by libguestfish.

Run this command as a temporary and immediate fix::

    sudo chmod 0644 /boot/vmlinuz-*
    for k in /boot/vmlinuz-*
        do sudo dpkg-statoverride --add --update root root 0644 /boot/vmlinuz-$k
    done

You likely want both this temporary fix and a more permanent fix; otherwise each
kernel update will revert to the default permissions and ExtractCode will stop
working for VM images extraction.

Therefore follow these instructions:

1. As sudo, create the file /etc/kernel/postinst.d/statoverride with this
content, devised by Kees Cook (@kees) in
https://bugs.launchpad.net/ubuntu/+source/linux/+bug/759725/comments/3 ::

    #!/bin/sh
    version="$1"
    # passing the kernel version is required
    [ -z "${version}" ] && exit 0
    dpkg-statoverride --update --add root root 0644 /boot/vmlinuz-${version}

2. Set executable permissions::

    sudo chmod +x /etc/kernel/postinst.d/statoverride

See also these links for a complete discussion:

    - https://bugs.launchpad.net/ubuntu/+source/linux/+bug/759725
    - https://bugzilla.redhat.com/show_bug.cgi?id=1670790
    - https://bugs.launchpad.net/ubuntu/+source/libguestfs/+bug/1813662/comments/24


Alternative
-----------

These other tools are related and were considered before creating ExtractCode:

These tools provide built-in, original extraction capabilities:

- https://libarchive.org/ (integrated in ExtractCode) (BSD license)
- https://www.7-zip.org/ (integrated in ExtractCode) (LGPL license)
- https://theunarchiver.com/command-line (maintenance status unknown) (LGPL license)

These tools are command line tools  wrapping other extraction tools and are
similar to ExtractCode but with different goals:

- https://github.com/wummel/patool (wrapper on many CLI tools) (GPL license)
- https://github.com/dtrx-py/dtrx (wrapper on a few CLI tools) (recently revived) (GPL license)
