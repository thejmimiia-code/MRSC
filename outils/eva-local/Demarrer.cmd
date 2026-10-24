@echo off
setlocal
cd /d "%~dp0"
echo EVA - essai de reconstruction 3D locale pour RTX 2070 Super 8 Go
echo.
echo Lisez d'abord le fichier LISEZ-MOI.txt.
echo Ce lancement installe des logiciels dans votre profil utilisateur
echo et telecharge les poids officiels. Vos images sont traitees localement.
echo Le resultat sera une reconstruction NON RIGGEE a examiner, pas EVA finalisee.
echo Aucune modification globale de PowerShell, aucun achat, aucun redemarrage.
echo.
choice /C ON /N /M "Autoriser cette installation et cet essai (O/N) ? "
if errorlevel 2 exit /b 0
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Lancer-Eva.ps1" -Installer -Generer -AccepterLicence
set RESULT=%ERRORLEVEL%
echo.
if not "%RESULT%"=="0" echo Le lancement a ete interrompu. Aucun modele final n'est annonce.
pause
exit /b %RESULT%
