@echo off
set SCRIM_LOG=%temp%\cons_install_log.txt
set SCRIM_PATH=%temp%\cons_post_install.bat
set SCRIM_SCRIPT=%0


REM Check for administrative rights
net session >nul 2>&1 && (
    set SCRIM_ADMIN=1
) || (
    set SCRIM_ADMIN=0
)


if exist %SCRIM_PATH% (
    del %SCRIM_PATH%
)

python -m install %*

if exist %SCRIM_PATH% (
    goto :try
) else (
    goto :finally
)


:try
call %SCRIM_PATH% 2> %SCRIM_LOG%
if errorlevel 1 (
    goto :except
) else (
    goto :finally
)


:except
set /p commands=<%SCRIM_PATH%
set /p err=<%SCRIM_LOG%
del %SCRIM_LOG%
echo Error:
echo:
echo %commands%
echo:
echo Failed with:
echo:
echo %err%
goto :finally


:finally
if exist %SCRIM_PATH% (
    del %SCRIM_PATH%
)


set SCRIM_LOG=
set SCRIM_PATH=
set SCRIM_SCRIPT=
set SCRIM_ADMIN=
