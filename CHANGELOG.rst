Changelog
=========

v (next)
--------


v21.6.2
-------

- Add new --list-formats command line option to list supported archive formats
- Add new exttractcode.api.extract_archive() API function to extract a single
  archive file of any supported format, non recursively.


v21.6.1
-------

- Add support for VMDK, QCOW and VDI VM image filesystems extraction
- Add new configuration mechanism to get third-party binary paths:

  - Use an environment variable
  - Or use a plugin-provided path
  - Or use well-known system installation locations
  - Or use the system PATH
  - Or fail with an informative error message

- Update to use latest skeleton


v21-2-24
----------

- Fix incorrect documentation link


v21-1-21
----------

- Fix bug related to CommonCode libraries loading
- Improve the extra requirements
- Set minimum version for dependencies
- Improve documentation
- Reorganize tests files


v21-1-15
----------

- Drop support for Python 2
- Use the latest CommonCode and TypeCode libraries
- Add azure-pipelines CI support


v20.10
------

- Initial release as a split from ScanCode toolkit
