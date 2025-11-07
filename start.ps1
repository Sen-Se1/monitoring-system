Write-Host "🚀 Démarrer le script du système de surveillance..."

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python n'est pas installé. Installation..."
    winget install -e --id Python.Python.3.12
}

if (-not (Test-Path "venv")) {
    Write-Host "📦 Création de l'environnement virtuel..."
    python -m venv venv
}

Write-Host "🎯 Activation de l'environnement virtuel..."
& "$PWD\venv\Scripts\Activate.ps1"

Write-Host "📦 Installation des dépendances..."
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
} else {
    Write-Host "❌ requirements.txt introuvable!"
    exit 1
}

Write-Host "📁 Création des dossiers..."
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

python run_monitoring_with_dashboard.py
