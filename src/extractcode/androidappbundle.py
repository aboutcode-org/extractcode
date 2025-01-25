#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/extractcode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import logging
import os
import zipfile
import attr

from extractcode import ExtractErrorFailedToExtract

"""
Support to extract Android App Bundle (.aab) files.
"""

logger = logging.getLogger(__name__)

TRACE = False

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)


@attr.s
class AndroidAppBundle:
    location = attr.ib()
    extracted_dir = attr.ib(default=None)

    @classmethod
    def from_file(cls, location):
        """
        Build a new AndroidAppBundle from the file at location.
        Raise exceptions on errors.
        """
        assert location
        abs_location = os.path.abspath(os.path.expanduser(location))

        if not os.path.exists(abs_location):
            raise ExtractErrorFailedToExtract(
                f'The system cannot find the path specified: {abs_location}')

        if not is_aab(abs_location):
            raise ExtractErrorFailedToExtract(
                f'Unsupported file format: {abs_location}. Expected an Android App Bundle (.aab).')

        return cls(location=abs_location)

    def extract(self, target_dir):
        """
        Extract the Android App Bundle (.aab) file to the target directory.
        Return a dictionary mapping file paths to their sizes.
        Raise exceptions on errors.
        """
        assert target_dir
        abs_target_dir = os.path.abspath(os.path.expanduser(target_dir))

        if not os.path.exists(abs_target_dir) or not os.path.isdir(abs_target_dir):
            raise ExtractErrorFailedToExtract(
                f'The system cannot find the target directory path specified: {target_dir}')

        try:
            with zipfile.ZipFile(self.location, 'r') as zip_ref:
                zip_ref.extractall(abs_target_dir)
            self.extracted_dir = abs_target_dir

            # Generate a file map of extracted files and their sizes
            file_map = {}
            for root, _, files in os.walk(abs_target_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    # Normalize the path to use forward slashes
                    relative_path = os.path.relpath(file_path, abs_target_dir).replace(os.sep, '/')
                    file_map[relative_path] = file_size

            return file_map
        except Exception as e:
            raise ExtractErrorFailedToExtract(f'Failed to extract {self.location}: {e}')
    
    def show_file_map(self):
        """
        Show the file map of extracted files and their sizes.
        """
        if not self.extracted_dir:
            raise ExtractErrorFailedToExtract('No files have been extracted yet.')

        # Generate the file map dynamically
        file_map = {}
        for root, _, files in os.walk(self.extracted_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                relative_path = os.path.relpath(file_path, self.extracted_dir)
                file_map[relative_path] = file_size

        # Print the file map
        for file_path, file_size in file_map.items():
            print(f'{file_path} ({file_size} bytes)')


def is_aab(file_path):
    """
    Check if a file is an Android App Bundle (.aab) by checking its extension.
    """
    return file_path.endswith('.aab')


def extract(location, target_dir):
    """
    Extract an Android App Bundle (.aab) file at ``location`` to the ``target_dir`` directory.
    Return a dictionary mapping file paths to their sizes.
    Raise Exception on errors.
    """
    assert target_dir
    abs_target_dir = os.path.abspath(os.path.expanduser(target_dir))

    if not os.path.exists(abs_target_dir) or not os.path.isdir(abs_target_dir):
        raise ExtractErrorFailedToExtract(
            f'The system cannot find the target directory path specified: {target_dir}')

    aab = AndroidAppBundle.from_file(location)
    return aab.extract(abs_target_dir)