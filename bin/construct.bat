@echo off
call :setdefault PY_ENTRY_POINT pyconstruct.exe
call :setdefault SCRIM_AUTO_WRITE 1
call :setdefault SCRIM_LOG %temp%\scrim_log.txt
call :setdefault SCRIM_PATH %temp%\scrim_out.bat
call :setdefault SCRIM_SCRIPT %0
call :setdefault SCRIM_SHELL cmd.exe
call :setdefault SCRIM_DEBUG 0

call :debug "Variables:"
call :debug "  SCRIM_AUTO_WRITE: %SCRIM_AUTO_WRITE%"
call :debug "        SCRIM_PATH: %SCRIM_PATH%"
call :debug "      SCRIM_SCRIPT: %SCRIM_SCRIPT%"
call :debug "       SCRIM_SHELL: %SCRIM_SHELL%"
call :debug "       SCRIM_DEBUG: %SCRIM_DEBUG%"
call :debug "executing %PY_ENTRY_POINT%"

%PY_ENTRY_POINT% %*

if exist %SCRIM_PATH% (
    goto :try
) else (
    goto :finally
)


:debug
if %SCRIM_DEBUG%==1 ( echo [scrim] %~1 )
goto :eof


:setdefault
if not defined %1 (
    set LOCAL_%1=1
    set %1=%2
)
goto :eof


:unset
if defined LOCAL_%1 (
    set LOCAL_%1=
    set %1=
)
goto :eof


:try
call :debug "found %SCRIM_PATH%"
call :debug "executing %SCRIM_PATH%"
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
echo [scrim] error executing:
echo:
echo %commands%
echo:
echo [scrim] failed with:
echo:
echo %err%
goto :finally


:finally
if exist %SCRIM_PATH% (
    call :debug "Removing %SCRIM_PATH%"
    del %SCRIM_PATH%
)


call :unset SCRIM_AUTO_WRITE
call :unset SCRIM_LOG
call :unset SCRIM_PATH
call :unset SCRIM_SCRIPT
call :unset SCRIM_SHELL
call :unset SCRIM_DEBUG
