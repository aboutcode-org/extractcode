#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/extractcode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import locale
import os
import subprocess
import sys
import time
import zipfile
from unittest import mock

import pytest

from commoncode import date as commoncode_date
from commoncode import fileutils
from commoncode.system import on_windows

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


class TestExtractionEnvironment(BaseArchiveTestCase):
    """
    Importing or using libarchive2 must not change the timezone or locale of the
    calling application. See https://github.com/aboutcode-org/extractcode/issues/65
    """

    # A POSIX-style TZ that is not UTC and has no DST
    local_tz = "EST+05"

    def setUp(self):
        self.original_locale = locale.setlocale(locale.LC_ALL)

    def tearDown(self):
        locale.setlocale(locale.LC_ALL, self.original_locale)
        # reload the TZ restored by mock.patch.dict in the C library
        if hasattr(time, "tzset"):
            time.tzset()

    def make_zip_with_local_date(self):
        # zipfile only stores a DOS date which is in local time: libarchive
        # converts it to a timestamp using the current TZ
        test_file = os.path.join(self.get_temp_dir(), "dos_date.zip")
        with zipfile.ZipFile(test_file, "w") as zf:
            zf.writestr(zipfile.ZipInfo("a.txt", date_time=(2020, 1, 2, 3, 4, 6)), "a")
        return test_file

    def test_importing_libarchive2_does_not_change_timezone_or_locale(self):
        code = (
            "import locale, os\n"
            "locale.setlocale(locale.LC_ALL, 'C')\n"
            "import extractcode.libarchive2\n"
            "assert os.environ['TZ'] == 'EST+05', os.environ['TZ']\n"
            "assert locale.setlocale(locale.LC_ALL) == 'C', locale.setlocale(locale.LC_ALL)\n"
        )
        env = dict(os.environ, TZ=self.local_tz)
        result = subprocess.run(
            [sys.executable, "-c", code], env=env, capture_output=True, text=True
        )
        assert result.returncode == 0, result.stderr

    def test_extract_restores_original_timezone_and_locale(self):
        from extractcode.libarchive2 import extract

        test_file = self.get_test_loc("archive/relative_path/basic.zip")
        test_dir = self.get_temp_dir()
        with mock.patch.dict(os.environ, {"TZ": self.local_tz}):
            locale.setlocale(locale.LC_ALL, "C")
            extract(test_file, test_dir)
            assert os.environ["TZ"] == self.local_tz
            assert locale.setlocale(locale.LC_ALL) == "C"

    def test_extract_does_not_set_timezone_when_originally_unset(self):
        from extractcode.libarchive2 import extract

        test_file = self.get_test_loc("archive/relative_path/basic.zip")
        test_dir = self.get_temp_dir()
        with mock.patch.dict(os.environ):
            os.environ.pop("TZ", None)
            extract(test_file, test_dir)
            assert "TZ" not in os.environ

    def test_extract_restores_original_timezone_and_locale_on_error(self):
        from extractcode.libarchive2 import ArchiveError
        from extractcode.libarchive2 import extract

        test_file = self.get_test_loc("archive/not_archive/wildtest.txt")
        test_dir = self.get_temp_dir()
        with mock.patch.dict(os.environ, {"TZ": self.local_tz}):
            locale.setlocale(locale.LC_ALL, "C")
            with pytest.raises(ArchiveError):
                extract(test_file, test_dir)
            assert os.environ["TZ"] == self.local_tz
            assert locale.setlocale(locale.LC_ALL) == "C"

    @pytest.mark.skipif(on_windows, reason="The C runtime caches the TZ on Windows")
    def test_extract_does_not_change_the_local_time_of_the_caller(self):
        # Run in a subprocess to check the timezone as cached by the C library
        # rather than only the TZ environment variable
        code = (
            "import sys, time\n"
            "from extractcode.libarchive2 import extract\n"
            "extract(sys.argv[1], sys.argv[2])\n"
            "assert time.localtime(0).tm_hour == 19, time.localtime(0)\n"
        )
        env = dict(os.environ, TZ=self.local_tz)
        args = [sys.executable, "-c", code, self.make_zip_with_local_date(), self.get_temp_dir()]
        result = subprocess.run(args, env=env, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr

    def test_extraction_environment_is_reentrant(self):
        from extractcode.libarchive2 import extraction_environment

        with mock.patch.dict(os.environ, {"TZ": self.local_tz}):
            with extraction_environment():
                with extraction_environment():
                    assert os.environ["TZ"] == "UTC"
                # still in an extraction: the original TZ is not restored yet
                assert os.environ["TZ"] == "UTC"
            assert os.environ["TZ"] == self.local_tz

    @pytest.mark.skipif(on_windows, reason="The C runtime caches the TZ on Windows")
    def test_extract_uses_utc_for_local_dates_regardless_of_the_local_timezone(self):
        from extractcode.libarchive2 import extract

        test_file = self.make_zip_with_local_date()
        test_dir = self.get_temp_dir()
        with mock.patch.dict(os.environ, {"TZ": self.local_tz}):
            extract(test_file, test_dir)
        result = commoncode_date.get_file_mtime(os.path.join(test_dir, "a.txt"))
        assert result == "2020-01-02 03:04:06"
