@echo off
setlocal

for /f "tokens=* delims=" %%a in ('date /t') do set current_date=%%a
for /f "tokens=* delims=" %%b in ('time /t') do set current_time=%%b

set "p=%~p0"
for %%A in (%p:\= %) do set "folder=%%~A"

:: Clean the old folder
rmdir /s /q dist
rmdir /s /q build
for /d %%i in (*.egg-info) do rmdir /s /q "%%i"
rmdir /s /q __pycache__

:: Run the Build
python setup.py sdist bdist_wheel
if errorlevel 1 (
    c:\TOOLS\ntfy_2.11.0_windows_amd64\ntfy.exe pub -t "Python: FAILED %current_date% %current_time%" -m "[%current_date% %current_time%] ❌ Build Failed: An error occurs when building package!" -i "https://image.pngaaa.com/287/1947287-middle.png" http://222.222.222.5:89/androcall

    sendgrowl %folder% BuildEvent "Build Failed" "An error occurs when building package!" -p 2
    exit /b 1
)

:: Upload ke repository
twine upload dist\* -r pypihub
if errorlevel 1 (
    c:\TOOLS\ntfy_2.11.0_windows_amd64\ntfy.exe pub -t "Python: FAILED %current_date% %current_time%" -m "[%current_date% %current_time%] ❌ Upload Failed: Failed to upload to the pypihub!" -i "https://image.pngaaa.com/287/1947287-middle.png" http://222.222.222.5:89/androcall

    sendgrowl %folder% UploadEvent "Upload Failed" "Failed to upload to the pypihub!" -p 2
)

twine upload dist\*
rem if errorlevel 1 (
rem     sendgrowl %folder% UploadEvent "Upload Failed" "Failed to upload to Pypi Default!" -p 2
rem     exit /b 1
rem )

:: If everything works
c:\TOOLS\ntfy_2.11.0_windows_amd64\ntfy.exe pub -t "Python: SUCCESS %current_date% %current_time%" -m "[%current_date% %current_time%] ✅ Build Success: Build and Upload SUCCESSFUL!" -i "https://image.pngaaa.com/287/1947287-middle.png" http://222.222.222.5:89/androcall

sendgrowl %folder% BuildEvent "Build Success" "Build and Upload SUCCESSFUL!" -p 0

endlocal
