#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/extractcode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

"""
Note: this API is unstable and still evolving.
"""


def extract_archives(
    location,
    recurse=True,
    replace_originals=False,
    ignore_pattern=(),
    all_formats=False,
):
    """
    Yield ExtractEvent while extracting archive(s) and compressed files at
    `location`.

    If `recurse` is True, extract nested archives-in-archives recursively.
    If `all_formats` is True, extract all supported archives formats.

    Archives and compressed files are extracted in a directory named
    "<file_name>-extract" created in the same directory as the archive.

    Note: this API is returning an iterable and NOT a sequence.
    """

    from extractcode.extract import extract
    from extractcode import default_kinds
    from extractcode import all_kinds

    kinds = all_kinds if all_formats else default_kinds

    for xevent in extract(
        location=location,
        kinds=kinds,
        recurse=recurse,
        replace_originals=replace_originals,
        ignore_pattern=ignore_pattern,
    ):
        yield xevent
