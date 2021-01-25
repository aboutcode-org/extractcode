
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

import os
import subprocess

import pytest

from commoncode.fileutils import as_posixpath
from commoncode.fileutils import resource_iter
from commoncode.testcase import FileDrivenTesting
from commoncode.system import on_windows

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

"""
These CLI tests are dependent on py.test monkeypatch to  ensure we are testing
the actual command outputs as if using a TTY or not.
"""


def run_extract(options, expected_rc=None, cwd=None):
    """
    Run extractcode as a plain subprocess. Return rc, stdout, stderr.
    """
    bin_dir = 'Scripts' if on_windows else 'bin'
    cmd_loc = os.path.join(project_root, 'tmp', bin_dir, 'extractcode')
    assert os.path.exists(cmd_loc + ('.exe' if on_windows else ''))
    args = [cmd_loc] + options
    result = subprocess.run(args,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        cwd=cwd,
        universal_newlines=True,
    )

    if expected_rc is not None and result.returncode != expected_rc:
        opts = ' '.join(options)
        error = f'''
Failure to run: extractcode {opts}:
stdout:
{result.stdout}

stderr:
{result.stderr}
'''
        assert result.returncode == expected_rc, error

    return result


def test_extractcode_command_can_take_an_empty_directory():
    test_dir = test_env.get_temp_dir()
    result = run_extract([test_dir], expected_rc=0)

    assert 'Extracting archives...' in result.stderr
    assert 'Extracting done' in result.stderr


def test_extractcode_command_does_extract_verbose():
    test_dir = test_env.get_test_loc('cli/extract', copy=True)
    result = run_extract(['--verbose', test_dir], expected_rc=1)

    assert os.path.exists(os.path.join(test_dir, 'some.tar.gz-extract'))
    assert 'Extracting archives...' in result.stderr
    assert 'some.tar.gz' in result.stdout
    assert 'broken.tar.gz' in result.stderr
    assert 'tarred_gzipped.tgz' in result.stdout
    assert 'ERROR extracting' in result.stderr
    assert "broken.tar.gz: Unrecognized archive format" in result.stderr
    assert 'Extracting done.' in result.stderr


def test_extractcode_command_always_shows_something_if_not_using_a_tty_verbose_or_not():
    test_dir = test_env.get_test_loc('cli/extract/some.tar.gz', copy=True)

    result = run_extract(options=['--verbose', test_dir], expected_rc=0)
    assert 'Extracting archives...' in result.stderr
    assert 'Extracting: some.tar.gz' in result.stdout
    assert 'Extracting done.' in result.stderr

    result = run_extract(options=[test_dir], expected_rc=0)
    assert 'Extracting archives...' in result.stderr
    assert 'Extracting done.' in result.stderr


def test_extractcode_command_works_with_relative_paths():
    # The setup is complex because we want to have a relative dir to the base
    # dir where we run tests from, i.e. the git checkout  dir To use relative
    # paths, we use our tmp dir at the root of the code tree
    from os.path import join
    from  commoncode import fileutils
    import extractcode
    import tempfile
    import shutil

    try:
        test_file = test_env.get_test_loc('cli/extract_relative_path/basic.zip')

        project_tmp = join(project_root, 'tmp')
        fileutils.create_dir(project_tmp)
        temp_rel = tempfile.mkdtemp(dir=project_tmp)
        assert os.path.exists(temp_rel)

        relative_dir = temp_rel.replace(project_root, '').strip('\\/')
        shutil.copy(test_file, temp_rel)

        test_src_file = join(relative_dir, 'basic.zip')
        test_tgt_dir = join(project_root, test_src_file) + extractcode.EXTRACT_SUFFIX
        result = run_extract([test_src_file], expected_rc=0, cwd=project_root)

        assert 'Extracting done' in result.stderr
        assert not 'WARNING' in result.stderr
        assert not 'ERROR' in result.stderr

        expected = ['/c/a/a.txt', '/c/b/a.txt', '/c/c/a.txt']
        file_result = [
            as_posixpath(f.replace(test_tgt_dir, ''))
            for f in fileutils.resource_iter(test_tgt_dir, with_dirs=False)]

        assert sorted(expected) == sorted(file_result)

    finally:
        fileutils.delete(relative_dir)


def test_extractcode_command_works_with_relative_paths_verbose():
    # The setup is a tad complex because we want to have a relative dir
    # to the base dir where we run tests from, i.e. the git checkout dir
    # To use relative paths, we use our tmp dir at the root of the code tree
    from os.path import join
    from  commoncode import fileutils
    import tempfile
    import shutil

    try:
        project_tmp = join(project_root, 'tmp')
        fileutils.create_dir(project_tmp)
        test_src_dir = tempfile.mkdtemp(dir=project_tmp).replace(project_root, '').strip('\\/')
        test_file = test_env.get_test_loc('cli/extract_relative_path/basic.zip')
        shutil.copy(test_file, test_src_dir)
        test_src_file = join(test_src_dir, 'basic.zip')

        result = run_extract(['--verbose', test_src_file] , expected_rc=0)

        # extract the path from the second line of the output
        # check that the path is relative and not absolute
        lines = result.stderr.splitlines(False)
        line = lines[1]
        line_path = line.split(':', 1)[-1].strip()
        if on_windows:
            drive = test_file[:2]
            assert not line_path.startswith(drive)
        else:
            assert not line_path.startswith('/')
    finally:
        fileutils.delete(test_src_dir)


def test_usage_and_help_return_a_correct_script_name_on_all_platforms():
    options = ['--help']

    result = run_extract(options , expected_rc=0)

    assert 'Usage: extractcode [OPTIONS]' in result.stdout
    # this was showing up on Windows
    assert 'extractcode-script.py' not in result.stderr

    result = run_extract([])
    assert 'Usage: extractcode [OPTIONS]' in result.stderr
    # this was showing up on Windows
    assert 'extractcode-script.py' not in result.stderr

    result = run_extract(['-xyz'] , expected_rc=2)
    # this was showing up on Windows
    assert 'extractcode-script.py' not in result.stderr


def test_extractcode_command_can_extract_archive_with_unicode_names_verbose():
    test_dir = test_env.get_test_loc('cli/unicodearch', copy=True)
    result = run_extract(['--verbose', test_dir] , expected_rc=0)
    assert 'Sanders' in result.stdout

    file_result = [
        f for f in map(as_posixpath, resource_iter(test_dir, with_dirs=False))
        if not f.endswith('unicodepath.tgz')]
    file_result = [''.join(f.partition('/unicodepath/')[1:]) for f in file_result]
    file_result = [f for f in file_result if f]
    expected = [
        '/unicodepath/Ho_',
        '/unicodepath/Ho_a',
        '/unicodepath/koristenjem_Karkkainen_-_Sander.pdf'
    ]
    assert sorted(expected) == sorted(file_result)


def test_extractcode_command_can_extract_archive_with_unicode_names():
    test_dir = test_env.get_test_loc('cli/unicodearch', copy=True)
    run_extract([test_dir] , expected_rc=0)

    file_result = [
        f for f in map(as_posixpath, resource_iter(test_dir, with_dirs=False))
        if not f.endswith('unicodepath.tgz')]
    file_result = [''.join(f.partition('/unicodepath/')[1:]) for f in file_result]
    file_result = [f for f in file_result if f]
    expected = [
        '/unicodepath/Ho_',
        '/unicodepath/Ho_a',
        '/unicodepath/koristenjem_Karkkainen_-_Sander.pdf'
    ]
    assert sorted(expected) == sorted(file_result)


def test_extractcode_command_can_extract_shallow():
    test_dir = test_env.get_test_loc('cli/extract_shallow', copy=True)
    run_extract(['--shallow', test_dir] , expected_rc=0)

    file_result = [
        f for f in map(as_posixpath, resource_iter(test_dir, with_dirs=False))
        if not f.endswith('unicodepath.tgz')]
    file_result = [''.join(f.partition('/top.zip-extract/')[1:]) for f in file_result]
    file_result = [f for f in file_result if f]
    # this checks that the zip in top.zip are not extracted
    expected = [
        '/top.zip-extract/some3.zip',
        '/top.zip-extract/some2.zip',
        '/top.zip-extract/some1.zip',
    ]
    assert sorted(expected) == sorted(file_result)


def test_extractcode_command_can_ignore():
    test_dir = test_env.get_test_loc('cli/extract_ignore', copy=True)
    run_extract(['--ignore', '*.tar', test_dir] , expected_rc=0)

    file_result = [
        f for f in map(as_posixpath, resource_iter(test_dir, with_dirs=False))
        if not f.endswith('a.tar') or not f.endswith('b.tar')]
    file_result = [''.join(f.partition('/a.zip-extract/')[1:]) for f in file_result]
    file_result = [f for f in file_result if f]
    expected = [
        '/a.zip-extract/a.txt',
        '/a.zip-extract/b.zip',
        '/a.zip-extract/b.zip-extract/b.txt',
        '/a.zip-extract/c.tar',
    ]
    assert sorted(expected) == sorted(file_result)


@pytest.mark.skipif(on_windows, reason='FIXME: this test fails on Windows until we have support for long file names.')
def test_extractcode_command_can_extract_nuget():
    test_dir = test_env.get_test_loc('cli/extract_nuget', copy=True)
    result = run_extract(['--verbose', test_dir])

    if result.returncode != 0:
        print(result.stdout)
    assert 'ERROR extracting' not in result.stdout
    assert 'ERROR extracting' not in result.stderr
