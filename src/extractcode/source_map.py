#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/extractcode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
import os.path
import posixpath

from commoncode import fileutils
from commoncode import paths

import extractcode

"""
Utilities to parse source map files and treat them as if they were
archives containing files.
"""


def extract(location, target_dir):
    """
    Extract each source in sourcesContent list of a map file at `location` as
    files in a target_dir directory tree mimicking the directory in which the
    sources would be present.
    
    Return a list of warning messages. Raise Exception errors.
    """
    for path, content in extract_source_content_from_map(location):
        # Convert path to safe posix path
        map_subfile_path = paths.safe_path(path, preserve_spaces=True)

        # Create directories
        parent_dir = posixpath.dirname(map_subfile_path)
        parent_target_dir = os.path.join(target_dir, parent_dir)
        fileutils.create_dir(parent_target_dir)

        subfile_path = os.path.join(target_dir, map_subfile_path)
        with open(subfile_path, "w") as subfile:
            subfile.write(content)

        return []


def extract_source_content_from_map(location):
    """
    Return a list of tuples of (source, content)
    for each source in sourcesContent of a map file at location.

    Raise an exception if the file is not a JSON file or cannot be parsed.
    """
    try:
        with open(location, "r") as map_file:
            map_data = json.load(map_file)
    except json.JSONDecodeError as e:
        msg = f"Unable to decode map file:{location} {e}"
        raise extractcode.ExtractErrorFailedToExtract(msg)

    if "sourcesContent" in map_data:
        sources_content = map_data["sourcesContent"]
        sources = map_data.get("sources", [])

        # Inconsistent source map. In a valid source map, each entry in the ``sources``
        # list should have a corresponding entry in the ``sourcesContent`` list.
        # Use dummy filenames as `source` path in such scenario.
        if len(sources) != len(sources_content):
            sources = [
                f"source_content{i + 1}.txt" for i in range(len(sources_content))
            ]

        sources_and_content = list(zip(sources, sources_content))
        return sources_and_content

    return []
