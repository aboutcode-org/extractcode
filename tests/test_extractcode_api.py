# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/extractcode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from commoncode import fileutils

import extractcode
from extractcode import extract
from extractcode import api
from extractcode_assert_utils import check_files
from extractcode_assert_utils import BaseArchiveTestCase

project_root = os.path.dirname(os.path.dirname(__file__))


class TestExtractApi(BaseArchiveTestCase):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_extract_archive(self):
        test_dir = self.get_test_loc('api/doc.docx', copy=True)
        base = fileutils.parent_directory(test_dir)
        expected = [
            'c/a/a.txt',
            'c/b/a.txt',
            'c/c/a.txt',
        ]

        cleaned_test_file = test_dir.replace(base, '')
        expected_event = [
            extract.ExtractEvent(source='doc.docx', target='doc.docx-extract', done=False, warnings=[], errors=[]),
            extract.ExtractEvent(source='doc.docx', target='doc.docx-extract', done=True, warnings=[], errors=[]),
        ]
        target = extractcode.get_extraction_path(test_dir)
        result = list(api.extract_archive(test_dir, target))
        result = [
            r._replace(
                source=cleaned_test_file,
                target=extractcode.get_extraction_path(cleaned_test_file))
            for r in result
        ]
        assert expected_event == result
        check_files(target, expected)
