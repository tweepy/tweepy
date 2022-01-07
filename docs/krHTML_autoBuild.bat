@echo off
echo.

title Automatic Korean HTML Builder - by pinkrabbit412

set SPHINXOPTS=-D language=ko
call ./make.bat html

echo.
echo [!] Korean(ko) version HTML build completed.
echo     Now you can close this automatic build file.
pause > nul
