ExtractCode
===========

- license: Apache-2.0
- copyright: copyright (c) nexB. Inc. and others
- homepage_url: https://github.com/nexB/extractcode
- keywords: archive, extraction, libarchive, 7zip, scancode-toolkit


ExtractCode is a universal archive extractor. It uses behind the scenes
multiple tools such as:

- the Python standard library, 
- a custom ctypes binding to libarchive,
- the 7zip command line
- optionally libguestfs on Linux

With these it is possible to extract a large number of common and

less common archives and compressed files. ExtractCode tries to extract things
in the same way on all OSes, including auto-renaming files that would not have
valid names on certain filesystems or when there are multiple copies of the same
path in a given archive (which is possible in a tar).

The extraction is driven from  a "voting" system that considers the
file extension(s) and name, the filetype and mimetype (using a ctypes
binding to libmagic) to select the most appropriate extractor or
decompressor function. It can handle multi-level archives such as tar.gz and
can extract recursively nested archives.


Visit https://aboutcode.org and https://github.com/nexB/ for support and download.

To set up the development environment::

    source configure

To run unit tests::

    pytest -vvs -n 2

To clean up development environment::

    ./configure --clean


To run the command line tool in the activated environment::

    ./extractcode -h


Adding support for VM images extraction
---------------------------------------

Adding support for VM images requires the manual installation of libguestfs
tools system package. This is suport on Linux only. On Debian and Ubuntu you can
use this::

    sudo apt-get install libguestfs-tools


On Ubuntu only, an additional manual step is required as the kernel executable
file cannot be read as required by libguestfish.

Run this command as a temporary and immediate fix::

    for k in /boot/vmlinuz-*
        do sudo dpkg-statoverride --add --update root root 0644 /boot/vmlinuz-$k
    done


But you likely want both this temporary fix and a permanent fix; otherwise each
kernel update will revert to the default permissions and extractcode will stop
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

See also for a complete discussion:

    - https://bugs.launchpad.net/ubuntu/+source/linux/+bug/759725
    - https://bugzilla.redhat.com/show_bug.cgi?id=1670790
    - https://bugs.launchpad.net/ubuntu/+source/libguestfs/+bug/1813662/comments/24


Configuration with environment variables
----------------------------------------

ExtractCode will use these environment variables if set:

- EXTRACTCODE_GUESTFISH_PATH : the path to the ``guestfish`` tool from
  libguestfs to use to extract VM images. If not provided, ExtractCode will look
  in the PATH for an installed ``guestfish`` executable instead.

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
  