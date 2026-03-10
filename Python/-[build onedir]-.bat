@echo off

pyinstaller ^
--onedir ^
--add-binary "ffmpeg.exe;." ^
--add-binary "ffprobe.exe;." ^
--noconsole ^
--icon=icon.ico ^
--distpath Build ^
--workpath Build\BuildTemp ^
--name "Quick_Audio" ^
main_update.py

rmdir /s /q Build\BuildTemp

echo.
echo Build finish. Press anything to exit...
pause