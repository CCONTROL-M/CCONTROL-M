function Ligar-Motores {
    Write-Host "Comando reconhecido: Ligar os motores" -ForegroundColor Green
    & "$PSScriptRoot\ligar_motores.cmd"
}

# Cria um alias para o comando
Set-Alias -Name "Ligar" -Value Ligar-Motores

# Define uma função para processar texto de entrada
function Processar-Comando {
    param (
        [string]$texto
    )
    
    if ($texto -like "*ligar os motores*") {
        Ligar-Motores
        return $true
    }
    return $false
}

# Mensagem de como usar
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "    Comando 'Ligar os motores' configurado!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para usar, você pode:" -ForegroundColor Yellow
Write-Host "1. Digitar 'Ligar' no PowerShell (depois de importar este arquivo)" -ForegroundColor Yellow
Write-Host "2. Digitar 'Ligar os motores' (depois de importar este arquivo)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Para importar este arquivo, execute:" -ForegroundColor Magenta
Write-Host ". .\comando_personalizado.ps1" -ForegroundColor Magenta
Write-Host ""

# Exporta as funções
Export-ModuleMember -Function Ligar-Motores, Processar-Comando -Alias Ligar 