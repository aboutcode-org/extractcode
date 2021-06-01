@echo OFF

@rem Copyright (c) nexB Inc. and others. All rights reserved.
@rem SPDX-License-Identifier: Apache-2.0
@rem See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
@rem ScanCode is a trademark of nexB Inc.
@rem See https://github.com/nexB/extractcode for support or download.
@rem See https://aboutcode.org for more information about nexB OSS projects.

@rem  A wrapper to ExtractCode command line entry point

set EXTRACTCODE_ROOT_DIR=%~dp0
set EXTRACTCODE_CONFIGURED_PYTHON=%EXTRACTCODE_ROOT_DIR%Scripts\python.exe

if not exist "%EXTRACTCODE_CONFIGURED_PYTHON%" goto configure
goto extractcode

:configure
echo * Configuring ExtractCode for first use...
set CONFIGURE_QUIET=1
call "%EXTRACTCODE_ROOT_DIR%configure"

@rem Return a proper return code on failure
if %errorlevel% neq 0 (
    exit /b %errorlevel%
)

:extractcode
@rem without this things may not always work on Windows 10, but this makes things slower
set PYTHONDONTWRITEBYTECODE=1

"%EXTRACTCODE_ROOT_DIR%Scripts\extractcode" %*
