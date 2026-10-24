# Tests Windows sans installer de modele, de pilote ou de dependance.
$ErrorActionPreference = 'Stop'
foreach ($Name in @('Lancer-Eva.ps1','Natif.ps1','Test-Lanceur.ps1')) {
    $Tokens = $null
    $ParseErrors = $null
    [System.Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot $Name),[ref]$Tokens,[ref]$ParseErrors) | Out-Null
    if ($ParseErrors.Count -gt 0) { $ParseErrors | Format-List; throw "Erreur de syntaxe : $Name" }
}
. (Join-Path $PSScriptRoot 'Natif.ps1')
Invoke-Checked $env:ComSpec @('/d','/c','exit 0')
$Caught = $false
try { Invoke-Checked $env:ComSpec @('/d','/c','exit 7') } catch { $Caught = $true }
if (-not $Caught) { throw 'Code non nul masque.' }
$Dir = Join-Path ([IO.Path]::GetTempPath()) ('eva test espaces '+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $Dir | Out-Null
try {
    $Child = Join-Path $Dir 'test arguments.ps1'
    Set-Content -Encoding ASCII -LiteralPath $Child -Value 'param([string]$Image); if ($Image -ne "reference avec espace.png") { exit 23 }; exit 0'
    $Shell = (Get-Process -Id $PID).Path
    Invoke-Checked $Shell @('-NoProfile','-File',$Child,'-Image','reference avec espace.png')
} finally {
    Remove-Item -LiteralPath $Dir -Recurse -Force
}
Write-Host 'Syntaxe PowerShell, propagation des echecs et arguments avec espaces : OK. Aucun test GPU effectue.'
