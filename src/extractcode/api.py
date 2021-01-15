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

"""
Note: this API is unstable and still evolving.
"""


def extract_archives(location, recurse=True, replace_originals=False, ignore_pattern=()):
    """
    Yield ExtractEvent while extracting archive(s) and compressed files at
    `location`. If `recurse` is True, extract nested archives-in-archives
    recursively.
    Archives and compressed files are extracted in a directory named
    "<file_name>-extract" created in the same directory as the archive.
    Note: this API is returning an iterable and NOT a sequence.
    """
    from extractcode.extract import extract
    from extractcode import default_kinds
    for xevent in extract(
        location=location,
        kinds=default_kinds,
        recurse=recurse,
        replace_originals=replace_originals,
        ignore_pattern=ignore_pattern
    ):
        yield xevent
