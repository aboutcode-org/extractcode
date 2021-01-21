
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

import click
from click.testing import CliRunner
import pytest

from commoncode.fileutils import as_posixpath
from commoncode.fileutils import resource_iter
from commoncode.testcase import FileDrivenTesting
from commoncode.system import on_linux
from commoncode.system import on_windows

from extractcode import cli

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

"""
These CLI tests are dependent on py.test monkeypatch to  ensure we are testing
the actual command outputs as if using a TTY or not.
"""


def test_extractcode_command_can_take_an_empty_directory(monkeypatch):
    test_dir = test_env.get_temp_dir()
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    runner = CliRunner()
    result = runner.invoke(cli.extractcode, [test_dir])
    assert result.exit_code == 0
    assert 'Extracting archives...' in result.output
    assert 'Extracting done' in result.output


def test_extractcode_command_does_extract_verbose(monkeypatch):
    test_dir = test_env.get_test_loc('cli/extract', copy=True)
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    runner = CliRunner()
    result = runner.invoke(cli.extractcode, ['--verbose', test_dir])
    assert result.exit_code == 1
    assert os.path.exists(os.path.join(test_dir, 'some.tar.gz-extract'))
    expected = [
        'Extracting archives...',
        'some.tar.gz',
        'broken.tar.gz',
        'tarred_gzipped.tgz',
        'ERROR extracting',
        "broken.tar.gz: Unrecognized archive format",
        'Extracting done.',
    ]
    for e in expected:
        assert e in result.output


def test_extractcode_command_always_shows_something_if_not_using_a_tty_verbose_or_not(monkeypatch):
    test_dir = test_env.get_test_loc('cli/extract/some.tar.gz', copy=True)
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: False)
    runner = CliRunner()
    result = runner.invoke(cli.extractcode, ['--verbose', test_dir])
    assert all(x in result.output for x in ('Extracting archives...', 'Extracting: some.tar.gz', 'Extracting done.'))
    result = runner.invoke(cli.extractcode, [test_dir])
    assert all(x in result.output for x in ('Extracting archives...', 'Extracting done.'))


def test_extractcode_command_works_with_relative_paths(monkeypatch):
    # The setup is a tad complex because we want to have a relative dir
    # to the base dir where we run tests from, i.e. the git checkout  dir
    # To use relative paths, we use our tmp dir at the root of the code tree
    from os.path import dirname, join, abspath
    from  commoncode import fileutils
    import extractcode
    import tempfile
    import shutil

    try:
        project_root = dirname(dirname(dirname(__file__)))
        project_tmp = join(project_root, 'tmp')
        fileutils.create_dir(project_tmp)
        project_root_abs = abspath(project_root)
        test_src_dir = tempfile.mkdtemp(dir=project_tmp).replace(project_root_abs, '').strip('\\/')
        test_file = test_env.get_test_loc('cli/extract_relative_path/basic.zip')
        shutil.copy(test_file, test_src_dir)
        test_src_file = join(test_src_dir, 'basic.zip')
        test_tgt_dir = join(project_root, test_src_file) + extractcode.EXTRACT_SUFFIX

        runner = CliRunner()
        monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
        result = runner.invoke(cli.extractcode, [test_src_file])
        assert result.exit_code == 0
        assert 'Extracting done' in result.output
        assert not 'WARNING' in result.output
        assert not 'ERROR' in result.output
        expected = ['/c/a/a.txt', '/c/b/a.txt', '/c/c/a.txt']
        file_result = [as_posixpath(f.replace(test_tgt_dir, '')) for f in fileutils.resource_iter(test_tgt_dir, with_dirs=False)]
        assert sorted(expected) == sorted(file_result)
    finally:
        fileutils.delete(test_src_dir)


def test_extractcode_command_works_with_relative_paths_verbose(monkeypatch):
    # The setup is a tad complex because we want to have a relative dir
    # to the base dir where we run tests from, i.e. the git checkout dir
    # To use relative paths, we use our tmp dir at the root of the code tree
    from os.path import dirname, join, abspath
    from  commoncode import fileutils
    import tempfile
    import shutil

    try:
        project_root = dirname(dirname(dirname(__file__)))
        project_tmp = join(project_root, 'tmp')
        fileutils.create_dir(project_tmp)
        project_root_abs = abspath(project_root)
        test_src_dir = tempfile.mkdtemp(dir=project_tmp).replace(project_root_abs, '').strip('\\/')
        test_file = test_env.get_test_loc('cli/extract_relative_path/basic.zip')
        shutil.copy(test_file, test_src_dir)
        test_src_file = join(test_src_dir, 'basic.zip')
        runner = CliRunner()
        monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
        result = runner.invoke(cli.extractcode, ['--verbose', test_src_file])
        assert result.exit_code == 0
        # extract the path from the second line of the output
        # check that the path is relative and not absolute
        lines = result.output.splitlines(False)
        line = lines[1]
        line_path = line.split(':', 1)[-1].strip()
        if on_windows:
            drive = test_file[:2]
            assert not line_path.startswith(drive)
        else:
            assert not line_path.startswith('/')
    finally:
        fileutils.delete(test_src_dir)


def test_usage_and_help_return_a_correct_script_name_on_all_platforms(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    runner = CliRunner()
    result = runner.invoke(cli.extractcode, ['--help'])
    assert 'Usage: extractcode [OPTIONS]' in result.output
    # this was showing up on Windows
    assert 'extractcode-script.py' not in result.output

    result = runner.invoke(cli.extractcode, [])
    assert 'Usage: extractcode [OPTIONS]' in result.output
    # this was showing up on Windows
    assert 'extractcode-script.py' not in result.output

    result = runner.invoke(cli.extractcode, ['-xyz'])
    # this was showing up on Windows
    assert 'extractcode-script.py' not in result.output


def test_extractcode_command_can_extract_archive_with_unicode_names_verbose(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('cli/unicodearch', copy=True)
    runner = CliRunner()
    result = runner.invoke(cli.extractcode, ['--verbose', test_dir])
    assert result.exit_code == 0

    assert 'Sanders' in result.output

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


def test_extractcode_command_can_extract_archive_with_unicode_names(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('cli/unicodearch', copy=True)
    runner = CliRunner()
    result = runner.invoke(cli.extractcode, [test_dir])
    assert result.exit_code == 0

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


def test_extractcode_command_can_extract_shallow(monkeypatch):
    test_dir = test_env.get_test_loc('cli/extract_shallow', copy=True)
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    runner = CliRunner()
    result = runner.invoke(cli.extractcode, ['--shallow', test_dir])
    assert result.exit_code == 0
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


def test_extractcode_command_can_ignore(monkeypatch):
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    test_dir = test_env.get_test_loc('cli/extract_ignore', copy=True)
    runner = CliRunner()
    result = runner.invoke(cli.extractcode, ['--ignore', '*.tar', test_dir])
    assert result.exit_code == 0

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
def test_extractcode_command_can_extract_nuget(monkeypatch):
    test_dir = test_env.get_test_loc('cli/extract_nuget', copy=True)
    monkeypatch.setattr(click._termui_impl, 'isatty', lambda _: True)
    runner = CliRunner()
    result = runner.invoke(cli.extractcode, ['--verbose', test_dir], catch_exceptions=False)
    if result.exit_code != 0:
        print(result.output)
    assert 'ERROR extracting' not in result.output
