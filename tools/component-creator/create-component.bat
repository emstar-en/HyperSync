@echo off
REM Component Creator Tool for HyperSync (Windows)
REM Usage: create-component.bat --name <component-name> --stage <experimental|stable|production> [OPTIONS]

setlocal enabledelayedexpansion

set COMPONENT_NAME=
set STAGE=
set DERIVED_FROM=
set TYPE=extension
set DOMAIN=

:parse_args
if "%~1"=="" goto validate_args
if "%~1"=="--name" (
    set COMPONENT_NAME=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--stage" (
    set STAGE=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--derived-from" (
    set DERIVED_FROM=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--type" (
    set TYPE=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--domain" (
    set DOMAIN=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="--help" goto show_usage
echo Unknown option: %~1
goto show_usage

:validate_args
if "%COMPONENT_NAME%"=="" goto show_usage
if "%STAGE%"=="" goto show_usage

if not "%STAGE%"=="experimental" if not "%STAGE%"=="stable" if not "%STAGE%"=="production" (
    echo Error: --stage must be experimental, stable, or production
    exit /b 1
)

set COMPONENT_PATH=components\%STAGE%\%COMPONENT_NAME%

if exist "%COMPONENT_PATH%" (
    echo Error: Component already exists at %COMPONENT_PATH%
    exit /b 1
)

echo Creating component: %COMPONENT_NAME%
echo Stage: %STAGE%
echo Type: %TYPE%
if not "%DERIVED_FROM%"=="" echo Derived from: %DERIVED_FROM%

mkdir "%COMPONENT_PATH%\specs" 2>nul
mkdir "%COMPONENT_PATH%\reference" 2>nul
mkdir "%COMPONENT_PATH%\generated" 2>nul
mkdir "%COMPONENT_PATH%\analysis\benchmarks" 2>nul
mkdir "%COMPONENT_PATH%\analysis\usage-patterns" 2>nul
mkdir "%COMPONENT_PATH%\analysis\feedback" 2>nul
mkdir "%COMPONENT_PATH%\docs" 2>nul
mkdir "%COMPONENT_PATH%\tests" 2>nul
mkdir "%COMPONENT_PATH%\examples" 2>nul

echo Created directory structure

for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set TODAY=%%c-%%a-%%b)

(
echo {
echo   "component": {
echo     "name": "%COMPONENT_NAME%",
echo     "full_name": "Component Full Name",
echo     "version": "0.1.0",
echo     "status": "%STAGE%",
echo     "maturity": "exploratory",
echo     "created": "%TODAY%",
echo     "last_updated": "%TODAY%"
echo   },
echo   "lifecycle": {
echo     "stage": "%STAGE%",
echo     "promotion_history": [],
echo     "next_review": "TBD"
echo   },
echo   "classification": {
echo     "type": "%TYPE%",
echo     "layer": "component-layer",
echo     "domain": []
echo   },
echo   "relationships": {
echo     "depends_on": [],
echo     "used_by": [],
echo     "integrates_with": [],
echo     "derived_from": %DERIVED_FROM:null=%,
echo     "derives": []
echo   },
echo   "files": {
echo     "specs": {
echo       "location": "./specs",
echo       "count": 0,
echo       "format": ["json"],
echo       "index": "./specs/index.json"
echo     },
echo     "reference": {
echo       "location": "./reference",
echo       "languages": [],
echo       "purpose": "Examples for STUNIR process",
echo       "note": "NOT generated code - reference implementations",
echo       "index": "./reference/index.json"
echo     },
echo     "generated": {
echo       "location": "./generated",
echo       "targets": [],
echo       "auto_generated": true,
echo       "do_not_edit": true
echo     },
echo     "analysis": {
echo       "location": "./analysis",
echo       "types": ["performance", "usage", "feedback"],
echo       "updated": "%TODAY%"
echo     }
echo   },
echo   "ai_metadata": {
echo     "keywords": [],
echo     "primary_functions": [],
echo     "use_cases": [],
echo     "complexity": "medium",
echo     "learning_curve": "moderate",
echo     "documentation_quality": "incomplete"
echo   },
echo   "development": {
echo     "active_work": true,
echo     "contributors": [],
echo     "issues_open": 0,
echo     "next_milestone": ""
echo   },
echo   "stunir": {
echo     "uses_stunir": false,
echo     "spec_to_ir": false,
echo     "ir_to_code": false,
echo     "targets": [],
echo     "last_generation": null
echo   }
echo }
) > "%COMPONENT_PATH%\meta.json"

echo Created meta.json

(
echo # %COMPONENT_NAME%
echo.
echo **Stage**: %STAGE%
echo **Type**: %TYPE%
if not "%DERIVED_FROM%"=="" echo **Derived from**: %DERIVED_FROM%
echo.
echo ## Overview
echo.
echo Brief description of what this component does.
echo.
echo ## Status
echo.
echo This component is currently in **%STAGE%** stage.
echo.
echo ## Directory Structure
echo.
echo - `specs/` - Component specifications
echo - `reference/` - Reference implementations
echo - `generated/` - STUNIR-generated code
echo - `analysis/` - Performance analysis
echo - `docs/` - Documentation
echo - `tests/` - Tests
echo - `examples/` - Examples
) > "%COMPONENT_PATH%\README.md"

echo # Specifications > "%COMPONENT_PATH%\specs\README.md"
echo # Reference Implementations > "%COMPONENT_PATH%\reference\README.md"
echo # Analysis > "%COMPONENT_PATH%\analysis\README.md"
echo # Documentation > "%COMPONENT_PATH%\docs\README.md"

echo.
echo Component created successfully at:
echo    %COMPONENT_PATH%
echo.
echo Next steps:
echo 1. Update meta.json with component details
echo 2. Add specifications to specs/
echo 3. Create reference implementations in reference/
echo 4. Document in docs/

exit /b 0

:show_usage
echo Usage: %~nx0 --name ^<component-name^> --stage ^<experimental^|stable^|production^> [OPTIONS]
echo.
echo Required:
echo   --name NAME           Component name (lowercase, hyphen-separated)
echo   --stage STAGE         Lifecycle stage: experimental, stable, or production
echo.
echo Optional:
echo   --derived-from PARENT Component this derives from
echo   --type TYPE          Component type: foundation, runtime, extension, tool
echo   --domain DOMAINS     Comma-separated domain keywords
echo   --help              Show this help message
echo.
echo Example:
echo   %~nx0 --name geometric-quantum --stage experimental --derived-from agua --type extension
exit /b 1
