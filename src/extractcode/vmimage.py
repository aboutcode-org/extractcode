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
import shutil
import warnings

from commoncode import command
from commoncode import fileutils
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


def get_command():
    """
    Return the location to the guestfish command or None.
    """
    cmd_loc = shutil.which('guestfish') or None
    if not cmd_loc:
        warnings.warn(GUESTFISH_NOT_FOUND)

    return cmd_loc


def extract(location, target_dir):
    """
    Extract all files from a guestfish-supported VM image archive file at
    location in the target_dir directory as a tarball.

    Return a list of warning messages if any or an empty list.
    Raise exception on errors.

    The extraction has a side effect to always create an intermediate tarball.
    This tarball will be created as a temporary file and deleted on success.

    This works only on Linux.
    """
    if not on_linux:
        raise ExtractErrorFailedToExtract(
            f'VM Image extraction only supported on Linux for: {location}')

    assert location
    abs_location = os.path.abspath(os.path.expanduser(location))
    if not os.path.exists(abs_location):
        raise ExtractErrorFailedToExtract(
            f'The system cannot find the path specified: {abs_location}')

    assert target_dir
    abs_target_dir = os.path.abspath(os.path.expanduser(target_dir))
    if not os.path.exists(abs_target_dir):
        raise ExtractErrorFailedToExtract(
            f'The system cannot find the target path specified: {target_dir}')

    cmd_loc = get_command()
    if not cmd_loc:
        raise ExtractErrorFailedToExtract(GUESTFISH_NOT_FOUND)

    supported_gfs_formats_by_extension = {
        '.qcow2': 'qcow2',
        '.vmdk': 'vmdk',
        '.vdi': 'vdi',
    }
    extension = fileutils.file_extension(location)
    image_format = supported_gfs_formats_by_extension.get(extension)

    if not image_format:
        raise ExtractErrorFailedToExtract(f'Unsupported image format: {location}')

    filename = fileutils.file_name(location)

    target_tarball = os.path.join(target_dir, f'{filename}.tar.gz')

    args = [
        '--ro',
        f'--format={image_format}',
        '--inspector',
        'tar-out',
        '--add' , location,
        '/', target_tarball,
        'compress:gzip',
    ]

    rc, stdout, stderr = command.execute2(cmd_loc=cmd_loc, args=args)

    if rc != 0:
        if TRACE:
            logger.debug(
                f'extract: failure: {rc}\n'
                f'stderr: {stderr}\n'
                f'stdout: {stdout}\n')
        error = f'{stdout}\n{stderr}'
        raise ExtractErrorFailedToExtract(error)

    return []
