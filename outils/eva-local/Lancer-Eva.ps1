# Windows 11, PowerShell 5.1+. Aucun changement de strategie d'execution global.
[CmdletBinding()]
param(
    [switch]$Installer,
    [switch]$Generer,
    [switch]$AccepterLicence,
    [string]$Image,
    [string]$DossierTravail = (Join-Path $env:LOCALAPPDATA 'MRSC-EVA'),
    [ValidateSet(128,192,256)][int]$Resolution = 256,
    [ValidateSet(512,1024,2048)][int]$Texture = 2048
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'Natif.ps1')

try {
    if (-not $env:LOCALAPPDATA) { throw 'Ce lanceur est destine a Windows.' }
    if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
        throw 'Python Launcher absent. Installez Python 3.11 x64 depuis python.org (avec le launcher), puis relancez. Aucun changement systeme effectue.'
    }
    & py -3.11 -c "import struct,sys; assert struct.calcsize('P')==8; print('Python',sys.version.split()[0])"
    if ($LASTEXITCODE -ne 0) { throw 'Python 3.11 x64 requis. Voir le guide joint ; ne pas utiliser le Python integre de Blender.' }
    $DossierTravail = [IO.Path]::GetFullPath($DossierTravail)
    $Venv = Join-Path $DossierTravail 'venv-py311'
    $Python = Join-Path $Venv 'Scripts\python.exe'
    $Worker = Join-Path $PSScriptRoot 'eva_local.py'
    if (-not $Image) {
        $BundleImage = Join-Path $PSScriptRoot 'references\eva-face-reference.png'
        $RepoImage = Join-Path $PSScriptRoot '..\..\assets\images\eva-references\eva-face-reference.png'
        if (Test-Path -LiteralPath $BundleImage) { $Image = $BundleImage } else { $Image = $RepoImage }
    }
    if ($Installer) {
        if (-not $AccepterLicence) { throw 'Lisez le guide et les licences. Utilisez -AccepterLicence pour autoriser installation et telechargement des dependances.' }
        New-Item -ItemType Directory -Force -Path $DossierTravail | Out-Null
        if (-not (Test-Path -LiteralPath $Python)) { Invoke-Checked 'py' @('-3.11','-m','venv',$Venv) }
        Invoke-Checked $Python @('-m','pip','install','pip==24.3.1','setuptools==75.6.0','wheel==0.45.1')
        # CUDA runtime inclus dans ces wheels ; pas de toolkit CUDA ni de WSL requis.
        Invoke-Checked $Python @('-m','pip','install','torch==2.6.0','torchvision==0.21.0','--index-url','https://download.pytorch.org/whl/cu118')
        Invoke-Checked $Python @('-m','pip','install','-r',(Join-Path $PSScriptRoot 'requirements-local.txt'))
        Invoke-Checked $Python @('-m','pip','check')
        & $Python -m pip freeze | Set-Content -Encoding UTF8 (Join-Path $DossierTravail 'versions-resolues.txt')
        if ($LASTEXITCODE -ne 0) { throw 'Impossible de consigner les versions.' }
    }
    if (-not (Test-Path -LiteralPath $Python)) { throw 'Environnement absent. Premier lancement : .\Lancer-Eva.ps1 -Installer -Generer -AccepterLicence' }
    Invoke-Checked $Python @($Worker,'--diagnostic','--cache',(Join-Path $DossierTravail 'cache'))
    if ($Generer) {
        if (-not $AccepterLicence) { throw 'Ajoutez -AccepterLicence apres lecture du guide. Les poids du modele seront telecharges.' }
        if (-not (Test-Path -LiteralPath $Image)) { throw "Reference introuvable. Passez -Image avec le chemin de la reference de face." }
        Invoke-Checked $Python @($Worker,'--generer','--accepter-licence','--image',([IO.Path]::GetFullPath($Image)),'--cache',(Join-Path $DossierTravail 'cache'),'--sortie',(Join-Path $DossierTravail 'resultats'),'--resolution',"$Resolution",'--texture',"$Texture")
    } else {
        Write-Host 'Diagnostic termine. Pour generer : ajoutez -Generer -AccepterLicence.'
    }
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
