# Appel natif sans construction de ligne de commande par concatenation.
function Invoke-Checked {
    param([string]$Exe, [string[]]$Arguments)
    & $Exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Commande interrompue (code $LASTEXITCODE). Aucun modele final annonce." }
}
