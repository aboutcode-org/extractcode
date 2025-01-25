#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/extractcode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
#from pathlib import Path

import pytest
import io
from contextlib import redirect_stdout

from extractcode_assert_utils import BaseArchiveTestCase
from extractcode_assert_utils import check_files

from extractcode import androidappbundle as aab_extractor


class TestExtractAAB(BaseArchiveTestCase):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_can_extract_aab_file(self):
        # Path to the test .aab file
        test_file = self.get_test_loc('androidappbundle/app-release.aab')
        target_dir = self.get_temp_dir('aab_extraction')

        # Extract the .aab file and get the file map
        file_map = aab_extractor.extract(test_file, target_dir)

        # Check if expected files are extracted
        expected_files = [
            'BUNDLE-METADATA/com.android.tools.build.libraries/dependencies.pb',
            'base/manifest/AndroidManifest.xml',
            'base/resources.pb',
            'BundleConfig.pb',
        ]
        # Verify that all expected files are in the file map
        for expected_file in expected_files:
            assert expected_file in file_map, f"Expected file {expected_file} not found in the file map"

        # Verify that the directories and files are physically created
        for expected_file in expected_files:
            # Construct the full path to the expected file
            full_path = os.path.join(target_dir, expected_file)
            # Check if the file exists
            assert os.path.exists(full_path), f"Expected file {full_path} does not exist"
            # Check if it is a file (not a directory)
            assert os.path.isfile(full_path), f"Expected file {full_path} is not a file"

        # Verify that the directories are created
        expected_directories = [
            'BUNDLE-METADATA',
            'BUNDLE-METADATA/com.android.tools.build.libraries',
            'base',
            'base/manifest',
        ]

        for expected_dir in expected_directories:
            # Construct the full path to the expected directory
            full_path = os.path.join(target_dir, expected_dir)
            # Check if the directory exists
            assert os.path.exists(full_path), f"Expected directory {full_path} does not exist"
            # Check if it is a directory
            assert os.path.isdir(full_path), f"Expected directory {full_path} is not a directory"

    def test_can_identify_aab_file(self):
        # Path to the test .aab file
        test_file = self.get_test_loc('androidappbundle/app-release.aab')

        # Check if the file is identified as an .aab file
        assert aab_extractor.is_aab(test_file) == True

    def test_extract_aab_invalid_file(self):
        # Create an invalid .aab file (not a zip file)
        invalid_file = os.path.join(self.get_temp_dir(), 'invalid.aab')
        with open(invalid_file, 'w') as f:
            f.write('This is not a valid .aab file')

        target_dir = self.get_temp_dir('aab_extraction_invalid')

        # Attempt to extract the invalid .aab file
        with pytest.raises(Exception):
            aab_extractor.extract(invalid_file, target_dir)

    def test_extract_aab_nonexistent_file(self):
        # Define a non-existent .aab file
        nonexistent_file = "nonexistent.aab"
        target_dir = self.get_temp_dir('aab_extraction_nonexistent')

        # Attempt to extract the non-existent .aab file
        with pytest.raises(aab_extractor.ExtractErrorFailedToExtract):
            aab_extractor.extract(nonexistent_file, target_dir)

    def test_show_file_map(self):
        # Path to the test .aab file
        test_file = self.get_test_loc('androidappbundle/app-release.aab')
        target_dir = self.get_temp_dir('aab_extraction')

        # Create an AndroidAppBundle instance and extract the .aab file
        aab = aab_extractor.AndroidAppBundle.from_file(test_file)
        file_map = aab.extract(target_dir)

        # Verify that the file map is not empty
        assert file_map, "File map should not be empty after extraction"

        # Call show_file_map() and capture the output
        output = io.StringIO()
        with redirect_stdout(output):
            aab.show_file_map()
        
        # Verify that the output contains expected files
        output_str = output.getvalue()
        expected_files = [
            'BUNDLE-METADATA/com.android.tools.build.libraries/dependencies.pb',
            'base/manifest/AndroidManifest.xml',
            'base/resources.pb',
            'BundleConfig.pb',
        ]
        for expected_file in expected_files:
            assert expected_file in output_str, f"Expected file {expected_file} not found in the output"