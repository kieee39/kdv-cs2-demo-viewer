@echo off
chcp 65001 >NUL
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
set "ROOT_DIR=%SCRIPT_DIR%"
set "PARSER_DIR=%ROOT_DIR%\kdv_parser"
set "KDV_DIR=%ROOT_DIR%\kdv"
set "PY_REQ=%KDV_DIR%\requirements.txt"
set "PY_VENV=%KDV_DIR%\.venv"

echo [KDV] Setting up Python virtual environment...
pushd "%ROOT_DIR%"
if not exist "%PY_VENV%\Scripts\activate.bat" (
    call python -m venv "%PY_VENV%"
    if errorlevel 1 exit /b !errorlevel!
)
call "%PY_VENV%\Scripts\activate.bat"
if errorlevel 1 exit /b !errorlevel!
echo [KDV] Installing Python dependencies...
call pip install -r "%PY_REQ%"
if errorlevel 1 exit /b !errorlevel!
popd

echo [KDV] Building Go parser (kdv_parser.exe)...
pushd "%PARSER_DIR%\cmd\parser\"
go build -trimpath -o "%KDV_DIR%\kdv_parser.exe" main.go
if errorlevel 1 exit /b !errorlevel!
popd

echo [KDV] Building KDV with PyInstaller...
pushd "%KDV_DIR%"
call "%PY_VENV%\Scripts\activate.bat"
if errorlevel 1 exit /b !errorlevel!
call pyinstaller --clean --distpath "." --workpath ".\\__pyinstaller__" ".\kdv.spec"
if errorlevel 1 exit /b !errorlevel!
popd
echo [KDV] Build finished.
endlocal
exit /b 0
