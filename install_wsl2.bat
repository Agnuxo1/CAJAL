@echo off
echo ========================================
echo Instalando WSL2 para CAJAL Training
echo ========================================
echo Habilitando features de Windows...
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
echo.
echo Instalando kernel update...
msiexec /i "D:\PROJECTS\CAJAL\wsl_update_x64.msi" /quiet /norestart
echo.
echo ========================================
echo WSL2 features habilitadas.
echo REINICIO REQUERIDO para completar la instalacion.
echo ========================================
pause