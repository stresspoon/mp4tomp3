@echo off
echo =========================================
echo MP4 to MP3 - Standalone EXE Builder
echo =========================================
echo.
echo This will create a single .exe file that
echo works without Python installation
echo.
echo Checking requirements...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed
    echo Please install Python to build the exe
    echo.
    echo Once built, the exe will work without Python
    pause
    exit /b 1
)

REM Install PyInstaller
echo Installing PyInstaller...
pip install pyinstaller pillow

REM Check ffmpeg.exe
if not exist ffmpeg.exe (
    echo.
    echo [ERROR] ffmpeg.exe not found!
    echo Please place ffmpeg.exe in this directory
    pause
    exit /b 1
)

REM Build the exe
echo.
echo Building standalone executable...
echo This may take a few minutes...
echo.

pyinstaller --onefile ^
            --windowed ^
            --name="MP4toMP3" ^
            --add-binary="ffmpeg.exe;." ^
            --hidden-import="tkinter" ^
            --hidden-import="tkinter.ttk" ^
            --hidden-import="tkinter.filedialog" ^
            --hidden-import="tkinter.messagebox" ^
            --clean ^
            --noupx ^
            converter_universal.py

if exist dist\MP4toMP3.exe (
    echo.
    echo =========================================
    echo BUILD SUCCESS!
    echo =========================================
    echo.
    echo Output: dist\MP4toMP3.exe
    echo Size: ~90-100 MB
    echo.
    echo This exe includes:
    echo - Python runtime
    echo - All required libraries
    echo - ffmpeg.exe
    echo.
    echo No installation needed!
    echo Just run MP4toMP3.exe
    echo =========================================

    echo.
    echo Packaging release zip...
    if exist dist\MP4toMP3_Windows.zip del /f /q dist\MP4toMP3_Windows.zip >nul 2>&1
    powershell -Command "Compress-Archive -Path 'dist/MP4toMP3.exe' -DestinationPath 'dist/MP4toMP3_Windows.zip' -Force"
    if exist dist\MP4toMP3_Windows.zip (
        echo Release zip created: dist\MP4toMP3_Windows.zip
    ) else (
        echo [WARN] Failed to create release zip. Please zip dist\MP4toMP3.exe manually.
    )
) else (
    echo.
    echo [ERROR] Build failed
    echo Check the error messages above
)

pause