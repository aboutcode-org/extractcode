#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/extractcode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
from unittest import mock

import pytest
from commoncode import fileutils

from extractcode_assert_utils import check_files
from extractcode_assert_utils import BaseArchiveTestCase

project_root = os.path.dirname(os.path.dirname(__file__))

"""
Minimal smoke tests for libarchive2.
"""


class TestExtractorTest(BaseArchiveTestCase):
    def test_libarchive_extract_can_extract_to_relative_paths(self):
        # The setup is a tad complex because we want to have a relative dir
        # to the base dir where we run tests from, i.e. the git checkout dir
        # To use relative paths, we use our tmp dir at the root of the code tree
        from os.path import join, abspath
        import tempfile
        import shutil
        from extractcode.libarchive2 import extract

        test_file = self.get_test_loc("archive/relative_path/basic.zip")
        project_tmp = join(project_root, "tmp")
        fileutils.create_dir(project_tmp)
        project_root_abs = abspath(project_root)
        test_src_dir = tempfile.mkdtemp(dir=project_tmp).replace(project_root_abs, "").strip("\\/")
        test_tgt_dir = tempfile.mkdtemp(dir=project_tmp).replace(project_root_abs, "").strip("\\/")
        shutil.copy(test_file, test_src_dir)
        test_src_file = join(test_src_dir, "basic.zip")
        result = list(extract(test_src_file, test_tgt_dir))
        assert [] == result
        expected = ["c/a/a.txt", "c/b/a.txt", "c/c/a.txt"]
        check_files(test_tgt_dir, expected)


class TestLoadLib:
    def _patch_locations(self, find_library):
        from extractcode import libarchive2

        return (
            mock.patch.dict(os.environ, {libarchive2.EXTRACTCODE_LIBARCHIVE_PATH_ENVVAR: ""}),
            mock.patch("plugincode.location_provider.get_location", return_value=None),
            mock.patch("ctypes.util.find_library", side_effect=find_library),
            mock.patch("commoncode.command.find_in_path", return_value=None),
        )

    def test_load_lib_finds_system_libarchive_by_its_library_name(self):
        from extractcode import libarchive2

        names = {"archive": "libarchive.so.13"}
        env, plugin, find_library, find_in_path = self._patch_locations(names.get)
        with env, plugin, find_library, find_in_path:
            with mock.patch("ctypes.cdll.LoadLibrary") as load_library:
                with pytest.warns(UserWarning):
                    result = libarchive2.load_lib()
        load_library.assert_called_once_with("libarchive.so.13")
        assert result is load_library.return_value

    def test_load_lib_fails_cleanly_when_no_system_libarchive_is_found(self):
        from extractcode import libarchive2

        env, plugin, find_library, find_in_path = self._patch_locations(lambda name: None)
        with env, plugin, find_library, find_in_path:
            with pytest.raises(Exception, match="libarchive DLL is not installed"):
                libarchive2.load_lib()
