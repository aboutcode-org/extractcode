#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/extractcode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
from pathlib import Path

import pytest

from commoncode.system import on_linux

from extractcode_assert_utils import BaseArchiveTestCase
from extractcode_assert_utils import check_files

from extractcode import vmimage

def is_kernel_readable():
    """
    Check if the kernel is readable by testing access to /boot/vmlinuz-*.
    Return True if readable, False otherwise.
    """
    if not os.name == "posix":
        return False  # Skip on non-Linux systems

    try:
        kernels = list(Path("/boot").glob("vmlinuz-*"))
        if not kernels:
            return False  # No kernel found
        return all(os.access(kern, os.R_OK) for kern in kernels)
    except Exception:
        return False  # Kernel check failed

@pytest.mark.skipif(not on_linux, reason='Only linux supports image extraction')
@pytest.mark.skipif(not is_kernel_readable(), reason="Kernel not readable")
class TestExtractVmImage(BaseArchiveTestCase):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_can_listfs_from_qcow2_image(self):
        test_file = self.extract_test_tar('vmimage/foobar.qcow2.tar.gz')
        test_file = str(Path(test_file) / 'foobar.qcow2')
        vmi = vmimage.VmImage.from_file(test_file)
        assert [('/dev/sda', 'ext2')] == vmi.listfs()

    def test_can_extract_qcow2_vm_image_as_tarball(self):
        test_file = self.extract_test_tar('vmimage/foobar.qcow2.tar.gz')
        test_file = str(Path(test_file) / 'foobar.qcow2')
        target_dir = self.get_temp_dir('vmimage')
        vmimage.extract(location=test_file, target_dir=target_dir, as_tarballs=True)
        expected = ['foobar.qcow2.tar.gz']
        check_files(target_dir, expected)

    def test_can_extract_qcow2_vm_image_not_as_tarball(self):
        test_file = self.extract_test_tar('vmimage/bios-tables-test.x86_64.iso.qcow2.tar.gz')
        test_file = str(Path(test_file) / 'bios-tables-test.x86_64.iso.qcow2')
        target_dir = self.get_temp_dir('vmimage')
        vmimage.extract(location=test_file, target_dir=target_dir, as_tarballs=False)
        expected = ['bios_tab.fat', 'boot.cat']
        check_files(target_dir, expected)
