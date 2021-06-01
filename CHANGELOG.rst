Changelog
=========

v (next)
--------


v21.6.1
--------

- Add support for VMDK, QCOW and VDI VM image filesystems extraction
- Add new configuration mechanism to get third-party binary paths:

  - Use an environment variable
  - Or use a plugin-provided path
  - Or use well-known system installation locations
  - Or use the system PATH
  - Or fail with an informative error message

- Update to use latest skeleton


v2021-2-24
----------

- Fix incorrect documentation link


v2021-1-21
----------

- Fix bug related to CommonCode libraries loading
- Improve the extra requirements
- Set minimum version for dependencies
- Improve documentation
- Reorganize tests files


v2021-1-15
----------

- Drop support for Python 2
- Use the latest CommonCode and TypeCode libraries
- Add azure-pipelines CI support


v20.10
------

- Initial release as a split from ScanCode toolkit
