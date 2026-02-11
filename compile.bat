@echo off

pyinstaller ^
--onefile ^
--noconsole ^
--icon=icon.ico ^
--distpath Compiled ^
--workpath Compiled\BuildTemp ^
Download_Lagu.py

rmdir /s /q Compiled\BuildTemp

echo.
echo Build selesai. Tekan tombol apa saja untuk keluar...
pause