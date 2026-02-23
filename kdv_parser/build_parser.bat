@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
for %%I in ("%SCRIPT_DIR%\..") do set "ROOT_DIR=%%~fI"

set "OUT_DIR=%ROOT_DIR%\kdv"
set "OUT_EXE=%OUT_DIR%\kdv_parser.exe"

if not exist "%OUT_DIR%" (
    mkdir "%OUT_DIR%"
)

echo [kdv_parser] Building parser...
pushd "%SCRIPT_DIR%"
go build -trimpath -o "%OUT_EXE%" ./cmd/parser
if errorlevel 1 (
    popd
    echo [kdv_parser] Build failed.
    exit /b 1
)
popd

echo [kdv_parser] Build succeeded: %OUT_EXE%
endlocal
exit /b 0
