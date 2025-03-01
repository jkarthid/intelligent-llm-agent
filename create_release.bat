@echo off
echo Creating a new release for Intelligent LLM Agent...
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Please run setup_venv.bat first.
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Run tests before release
echo.
echo Running tests before release...
python -m pytest || (
    echo Tests failed. Release creation aborted.
    call deactivate
    exit /b 1
)

REM Get current version from setup.py
for /f "tokens=2 delims==" %%a in ('findstr "version" setup.py') do (
    set CURRENT_VERSION=%%a
    set CURRENT_VERSION=!CURRENT_VERSION:"=!
    set CURRENT_VERSION=!CURRENT_VERSION:,=!
    set CURRENT_VERSION=!CURRENT_VERSION: =!
)

echo Current version: %CURRENT_VERSION%
echo.

REM Ask for new version
set /p NEW_VERSION=Enter new version (leave blank to use current version): 

if "%NEW_VERSION%"=="" (
    set NEW_VERSION=%CURRENT_VERSION%
)

echo.
echo Creating release version %NEW_VERSION%...

REM Update version in setup.py
echo Updating version in setup.py...
powershell -Command "(Get-Content setup.py) -replace 'version=\"[^\"]+\"', 'version=\"%NEW_VERSION%\"' | Set-Content setup.py"

REM Update CHANGELOG.md
echo Updating CHANGELOG.md...
echo.
echo Enter changelog entries for version %NEW_VERSION% (press Enter twice when done):
echo.

set CHANGELOG_ENTRY=## [%NEW_VERSION%] - %date:~10,4%-%date:~4,2%-%date:~7,2%\n\n### Added\n
set /p ADDED=- Added: 
if not "%ADDED%"=="" (
    set CHANGELOG_ENTRY=!CHANGELOG_ENTRY!- %ADDED%\n
)

set /p CHANGED=- Changed: 
if not "%CHANGED%"=="" (
    set CHANGELOG_ENTRY=!CHANGELOG_ENTRY!\n### Changed\n- %CHANGED%\n
)

set /p FIXED=- Fixed: 
if not "%FIXED%"=="" (
    set CHANGELOG_ENTRY=!CHANGELOG_ENTRY!\n### Fixed\n- %FIXED%\n
)

set /p REMOVED=- Removed: 
if not "%REMOVED%"=="" (
    set CHANGELOG_ENTRY=!CHANGELOG_ENTRY!\n### Removed\n- %REMOVED%\n
)

powershell -Command "$content = Get-Content -Raw CHANGELOG.md; $content -replace '## \[Unreleased\]', '## [Unreleased]\n\n%CHANGELOG_ENTRY%' | Set-Content CHANGELOG.md"

REM Create a tag
echo Creating git tag v%NEW_VERSION%...
git add setup.py CHANGELOG.md
git commit -m "Release version %NEW_VERSION%"
git tag -a v%NEW_VERSION% -m "Version %NEW_VERSION%"

echo.
echo Release v%NEW_VERSION% created!
echo.
echo To push the release to the remote repository, run:
echo git push origin main
echo git push origin v%NEW_VERSION%

REM Deactivate virtual environment
call deactivate
