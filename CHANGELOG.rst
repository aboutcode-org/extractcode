Changelog
=========

v31.0.0
--------

- Do not install patch.py by default. Instead this is now an extra


v30.0.0
--------

- Update to the latest skeleton. The virtualenv is now created under the venv
  directory with the ./configure --dev
- Switch back to semver versioning. Calver was not really needed here.
- Do not crash if there is a corrupted archive with the --replace-originals
  option

Thank you to:

- Jono Yang @JonoYang
- Bryan Sutula @sutula
- Smascer @Smascer
- Chin-Yeung Li @chinyeungli

v21.7.23
--------

- Spaces in file and directory names are no longer replaced by underscores when
  files and directories are extracted from archives.

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
