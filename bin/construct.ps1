function Debug([string]$msg){
    if ($env:SCRIM_DEBUG -eq 1) {
        Write-Host "[scrim] $msg"
    }
}


function Set-Default([string]$var, $value){
    # Sets environment variable only if it is undefined
    # If it is undefined create a new variable prefixed with LOCAL marking
    # that this var was created internally
    if(!(Test-Path Env:$var)){
        Set-Item Env:$var -value $value
        Set-Item Env:LOCAL_$var -value 1
    }
}


function Unset-Item([string]$var){
    # Remove environment variable only if it was previous marked local
    if(Test-Path Env:LOCAL_$var){
        Remove-Item Env:LOCAL_$var
        Remove-Item Env:$var
    }
}


$py_entry_point="pyconstruct.exe"
Set-Default SCRIM_AUTO_WRITE "1"
Set-Default SCRIM_PATH "$env:TEMP\scrim_out.ps1"
Set-Default SCRIM_SCRIPT $MyInvocation.MyCommand.Definition
Set-Default SCRIM_SHELL "powershell.exe"
Set-Default SCRIM_DEBUG 0


Debug "Variables:"
Debug "  SCRIM_AUTO_WRITE: $env:SCRIM_AUTO_WRITE"
Debug "        SCRIM_PATH: $env:SCRIM_PATH"
Debug "      SCRIM_SCRIPT: $env:SCRIM_SCRIPT"
Debug "       SCRIM_SHELL: $env:SCRIM_SHELL"
Debug "       SCRIM_DEBUG: $env:SCRIM_DEBUG"
Debug "executing $py_entry_point"

& $py_entry_point $args

if (Test-Path $env:SCRIM_PATH) {
    Debug "found $env:SCRIM_PATH"
    Debug "executing $env:SCRIM_PATH"
    Try{
        . "$env:SCRIM_PATH"
    }
    Catch {
        $ErrorItemName = $_.Exception.ItemName
        $ErrorMessage = $_.Exception.Message
        $commands = Get-Content $env:SCRIM_PATH | Out-String
        Write-Host '[scrim] error executing:'
        Write-Host ''
        Write-Host $commands
        Write-Host ''
        Write-Host '[scrim] failed with:'
        Write-Host ''
        Write-Host $ErrorItemName
        Write-Host $ErrorMessage
    }
    Debug "Removing $env:SCRIM_PATH"
    Remove-Item $env:SCRIM_PATH
}


Remove-Variable py_entry_point
Unset-Item SCRIM_AUTO_WRITE
Unset-Item SCRIM_DEBUG
Unset-Item SCRIM_PATH
Unset-Item SCRIM_SCRIPT
Unset-Item SCRIM_SHELL
