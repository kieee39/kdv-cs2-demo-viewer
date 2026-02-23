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
    python -m venv "%PY_VENV%"
)
call "%PY_VENV%\Scripts\activate.bat"
echo [KDV] Installing Python dependencies...
pip install -r "%PY_REQ%"
popd

echo [KDV] Building Go parser (kdv_parser.exe)...
pushd "%PARSER_DIR%\cmd\parser\"
go build -trimpath -o "%KDV_DIR%\kdv_parser.exe" main.go
popd

echo [KDV] Building KDV with PyInstaller...
pushd "%KDV_DIR%"
call "%PY_VENV%\Scripts\activate.bat"
pyinstaller --clean --distpath "." --workpath ".\\__pyinstaller__" ".\kdv.spec"
popd
echo [KDV] Build finished.
endlocal
exit /b 0
