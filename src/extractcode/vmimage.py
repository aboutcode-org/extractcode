#
# Copyright (c) nexB Inc. and others.
# SPDX-License-Identifier: Apache-2.0
#
# Visit https://aboutcode.org and https://github.com/nexB/ for support and download.
# ScanCode is a trademark of nexB Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging
import os
import pathlib
import shutil
import warnings

import attr

from commoncode import fileutils
from commoncode.text import as_unicode
from commoncode.system import on_linux

from extractcode import ExtractErrorFailedToExtract

"""
Support to extract Virtual Machine image formats and the filesystem(s) they
contain. This is based on libguestfs-tools and is tested only on Linux.
Works only if libguestfs tool guestfish is in the path.

See https://libguestfs.org/

On Ubuntu, you may face this issue when running guestfish:

- https://bugs.launchpad.net/ubuntu/+source/linux/+bug/759725
- https://bugs.launchpad.net/ubuntu/+source/libguestfs/+bug/1813662
- https://unix.stackexchange.com/a/642914/185837
"""

logger = logging.getLogger(__name__)

TRACE = False

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

GUESTFISH_NOT_FOUND = (
    'WARNING: guestfish executable is not installed. '
    'Unable to extract virtual machine image: you need to install the '
    'guestfish tool from libguestfs and extra FS drivers if needed. '
    'See https://libguestfs.org/ for details.'
)

EXTRACTCODE_GUESTFISH_PATH_ENVVAR = 'EXTRACTCODE_GUESTFISH_PATH'


def get_command(env_var=EXTRACTCODE_GUESTFISH_PATH_ENVVAR, command='guestfish'):
    """
    Return the location to the guestfish command or None.
    """
    cmd_loc = os.environ.get(env_var, None)
    if cmd_loc and os.path.exists(cmd_loc):
        return cmd_loc

    cmd_loc = shutil.which(command) or None
    if not cmd_loc:
        warnings.warn(GUESTFISH_NOT_FOUND)
    return cmd_loc


def check_linux_kernel_is_readable():
    """
    Return True if the kernel executable file can be read. This is required by
    guestfish and libguestfs and this is an oddity mostly on Ubuntu.

    See:
        - https://bugs.launchpad.net/ubuntu/+source/linux/+bug/759725
        - https://bugzilla.redhat.com/show_bug.cgi?id=1670790
        - https://bugs.launchpad.net/ubuntu/+source/libguestfs/+bug/1813662
    """
    error = (
        'libguestfs requires the kernel executable to be readable. '
        'This is the case on most Linux distribution except on Ubuntu.\n'
        'Run this command as a temporary fix:\n'
        '  for k in /boot/vmlinuz-*\n'
        '    do sudo dpkg-statoverride --add --update root root 0644 /boot/vmlinuz-$(uname -r)\n'
        '  done\n'
        'or:\n'
        '  sudo chmod +r /boot/vmlinuz-*\n\n',
        'For a permanent fix see: '
        'https://bugs.launchpad.net/ubuntu/+source/libguestfs/+bug/1813662/comments/21'
    )
    if on_linux:
        kernels = list(pathlib.Path('/boot').glob('vmlinuz-*'))
        if not kernels:
            raise ExtractErrorFailedToExtract(error)
        for kern in kernels:
            if not os.access(kern, os.R_OK):
                raise ExtractErrorFailedToExtract(
                    f'Unable to read kernel at: {kern}.\n{error}')


@attr.s
class VmImage:
    location = attr.ib()
    image_format = attr.ib()
    guestfish_command = attr.ib()

    @classmethod
    def from_file(cls, location):
        """
        Build a new VMImage from the file at location.
        Raise excptions on errors.
        """
        if not on_linux:
            raise ExtractErrorFailedToExtract('VM Image extraction only supported on Linux.')

        check_linux_kernel_is_readable()

        assert location
        abs_location = os.path.abspath(os.path.expanduser(location))

        if not os.path.exists(abs_location):
            raise ExtractErrorFailedToExtract(
                f'The system cannot find the path specified: {abs_location}')

        supported_gfs_formats_by_extension = {
            '.qcow2': 'qcow2',
            '.vmdk': 'vmdk',
            '.vdi': 'vdi',
        }

        extension = fileutils.file_extension(location)
        image_format = supported_gfs_formats_by_extension.get(extension)

        if not image_format:
            raise ExtractErrorFailedToExtract(f'Unsupported VM image format: {location}')

        cmd_loc = get_command()
        if not cmd_loc:
            raise ExtractErrorFailedToExtract(GUESTFISH_NOT_FOUND)

        return cls(
            location=location,
            image_format=image_format,
            guestfish_command=cmd_loc,
        )

    def listfs(self, skip_partitions=('swap',)):
        """
        Return a list of (filesystem /partition/ device path, filesystem type) for each
        filesystem found in this image .

        We run guestfish for this:
            $ guestfish --ro add foo.qcow2 : run : list-filesystems
            /partition/sda1: ext4
        """
        args = [
            '--ro',
            f'--format={self.image_format}',
            '--add' , self.location,
            'run',
            ':', 'list-filesystems',
        ]
        stdout = self.run_guestfish(args)

        filesystems = []
        entries = stdout.strip().splitlines(False)
        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue
            if ':' in entry:
                partition, _, fstype = entry.partition(':')
                fstype = fstype.strip()
            else:
                partition = entry
                fstype = None

            if any(s in partition for s in skip_partitions):
                continue

            filesystems.append((partition, fstype,))

        return filesystems

    def extract_image(self, target_tarball):
        """
        Extract all files from this VM image in the `target_tarball` file  as a
        gzipped-compressed tarball (.tar.gz). Raise exception on errors.
        """
        args = [
            '--ro',
            '--inspector',
            f'--format={self.image_format}',
            '--add', self.location,
            'tar-out', '/', target_tarball, 'compress:gzip',
        ]

        self.run_guestfish(args)

    def extract_partition(self, partition, target_tarball):
        """
        Extract all files from a single partition of this VM image to the
        `target_tarball` file as a gzipped-compressed tarball (.tar.gz). Raise
        exception on errors.
        """
        # TODO: there could be devices/partitions we do not want to extract?
        # guestfish --ro add foo.qcow2 : run : mount /dev/sda1 / : tar-out /etc foo.tgz compress:gzip

        args = [
            '--ro',
            f'--format={self.image_format}',
            '--add', self.location,
            'run',
            ':', 'mount', partition, '/',
            ':', 'tar-out', '/', target_tarball, 'compress:gzip',
        ]
        self.run_guestfish(args)

    def run_guestfish(self, args, timeout=None):
        """
        Run guestfish with `args` arguments.
        Return stdout as unicode string. Raise exception on error
        """
        import subprocess
        full_args = [self.guestfish_command] + args
        try:
            stdout = subprocess.check_output(full_args, timeout=timeout, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as cpe:
            args = ' '.join([self.guestfish_command] + args)
            output = as_unicode(cpe.output)
            error = f'Failed to run guestfish to extract VM image: {args}\noutput: {output}'
            raise ExtractErrorFailedToExtract(error)  # from cpe

        return as_unicode(stdout)


def extract(location, target_dir, as_tarballs=True):
    """
    Extract all files from a guestfish-supported VM image archive file at
    location in the target_dir directory. Optionally only extract the
    intermediate tarballs if `as_tarball` is True. Otherwise, extract to
    intermediate tarballs and then extract each tarballs to the final directory.

    Return a list of warning messages if any or an empty list.
    Raise exception on errors.
    This works only on Linux.
    """
    assert target_dir
    abs_target_dir = os.path.abspath(os.path.expanduser(target_dir))
    if not os.path.exists(abs_target_dir) or not os.path.isdir(abs_target_dir):
        raise ExtractErrorFailedToExtract(
            f'The system cannot find the target directory path specified: {target_dir}')

    vmimage = VmImage.from_file(location)

    warnings = []

    filename = fileutils.file_name(vmimage.location)

    # try a plain extract first
    try:

        if not as_tarballs:
            intermediate_dir = fileutils.get_temp_dir(prefix='extractcode-vmimage')
            tdir = intermediate_dir
        else:
            tdir = target_dir

        target_tarball = os.path.join(tdir, f'{filename}.tar.gz')
        vmimage.extract_image(target_tarball=target_tarball)

        if not as_tarballs:
            # extract the temp tarball to the final location
            warns = extract_image_tarball(
                tarball=target_tarball,
                target_dir=target_dir,
                skip_symlinks=False)
            warnings.extend(warns)

    except ExtractErrorFailedToExtract as e:
        print('Cannot extract VM Image filesystems as a single file tree.')

        warnings.append(f'Cannot extract VM Image filesystems as a single file tree:\n{e}')
        # fall back to file system extraction, one partition at a time
        partitions = vmimage.listfs()
        if not partitions:
            raise

        if len(partitions) == 1:
            # we can safely extract this to a root / dir as we have only one partition
            partition, _parttype = partitions[0]
            if not as_tarballs:
                intermediate_dir = fileutils.get_temp_dir(prefix='extractcode-vmimage')
                tdir = intermediate_dir
            else:
                tdir = target_dir

            target_tarball = os.path.join(tdir, f'{filename}.tar.gz')
            vmimage.extract_partition(partition=partition, target_tarball=target_tarball)

            if not as_tarballs:
                # extract the temp tarball to the final location
                warns = extract_image_tarball(
                    tarball=target_tarball,
                    target_dir=target_dir,
                    skip_symlinks=False)
                warnings.extend(warns)
        else:
            # with multiple partitions, we extract each partition to a unique
            # base name based after the partition device name

            for partition, _parttype in partitions:
                base_name = partition.replace('/', '-')

                if not as_tarballs:
                    intermediate_dir = fileutils.get_temp_dir(prefix='extractcode-vmimage')
                    tdir = intermediate_dir
                else:
                    tdir = target_dir

                partition_tarball = os.path.join(tdir, f'{filename}-{base_name}.tar.gz')
                vmimage.extract_partition(partition=partition, target_tarball=partition_tarball)

                if not as_tarballs:
                    # extract the temp tarball to the final location
                    # which is a new subdirectory
                    partition_target_dir = os.path.join(target_dir, base_name)
                    fileutils.create_dir(partition_target_dir)
                    warns = extract_image_tarball(
                        tarball=target_tarball,
                        target_dir=target_dir,
                        skip_symlinks=False)
                    warnings.extend(warns)

    return warnings


def extract_image_tarball(tarball, target_dir, skip_symlinks=False):
    """
    Extract an intermediate image tarball to its final directory.
    Return a list of warning messages
    """
    from extractcode.libarchive2 import extract
    return extract(
        location=tarball,
        target_dir=target_dir,
        skip_symlinks=skip_symlinks,
    )
