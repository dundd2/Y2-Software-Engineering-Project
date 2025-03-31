@echo off
setlocal EnableDelayedExpansion

echo Starting documentation build process...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    exit /b 1
)

REM Check if required Python packages are installed
echo Checking required packages...
python -c "import sphinx" >nul 2>&1 || (
    echo Installing sphinx...
    pip install sphinx sphinx_rtd_theme sphinxcontrib-plantuml
)

REM Clean up old build directories
echo Cleaning up old build files...
if exist "_build" (
    rmdir /s /q "_build" 2>nul
    if errorlevel 1 (
        echo Warning: Could not remove old _build directory. It may be in use.
        echo Please close any applications that might be using files in the _build directory.
        exit /b 1
    )
)

REM Clean up old PlantUML temp directories
for /d %%G in ("%TEMP%\sphinx_plantuml_*") do (
    rmdir /s /q "%%G" 2>nul
)

REM Set environment variables for PlantUML
set JAVA_OPTS=-Djava.awt.headless=true -Dfile.encoding=UTF-8
set PLANTUML_LIMIT_SIZE=8192

REM Check if Java is installed
java -version >nul 2>&1
if errorlevel 1 (
    echo Error: Java is not installed or not in PATH
    exit /b 1
)

REM Check if plantuml.jar exists
if not exist "plantuml.jar" (
    echo Error: plantuml.jar not found
    echo Please download plantuml.jar from https://plantuml.com/download
    exit /b 1
)

REM Check if Graphviz is installed (for PlantUML diagrams)
where dot >nul 2>&1
if errorlevel 1 (
    echo Warning: Graphviz is not installed. Some diagrams may not generate correctly.
    echo Please install Graphviz from https://graphviz.org/download/
)

echo Building documentation...

REM Run Sphinx build with increased verbosity
python -m sphinx -b html . _build/html -v

if errorlevel 1 (
    echo Build failed with error %errorlevel%
    echo Please check the error messages above
    exit /b %errorlevel%
)

REM Check if the build was successful
if not exist "_build\html\index.html" (
    echo Error: Build completed but index.html was not generated
    exit /b 1
)

echo Build completed successfully!
echo Documentation can be found in _build\html\index.html

REM Open the documentation in the default browser
start "" "_build\html\index.html"

pause