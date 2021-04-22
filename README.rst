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


Adding support for VM images
----------------------------

Adding support for VM images requires the manual installation of libguestfs and
it Python binding. You will need to install the libguestfs tools system package.
On Debian and Ubuntu::

    sudo apt-get install libguestfs-tools


On Ubuntu, a manual stpe is required if the kernel executable file cannot be read.
This is required by guestfish and libguestfs and this is an oddity there and not on Debian.

Run this command as a temporary fix::

    for k in /boot/vmlinuz-*
        do sudo dpkg-statoverride --add --update root root 0644 /boot/vmlinuz-$(uname -r)
    done

or::

    sudo chmod +r /boot/vmlinuz-*,


For a permanent fix see: 

    - https://bugs.launchpad.net/ubuntu/+source/libguestfs/+bug/1813662/comments/21

See also for a discussion:

    - https://bugs.launchpad.net/ubuntu/+source/linux/+bug/759725
    - https://bugzilla.redhat.com/show_bug.cgi?id=1670790
    - https://bugs.launchpad.net/ubuntu/+source/libguestfs/+bug/1813662



