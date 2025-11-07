#!/bin/bash

echo "🚀 Démarrer le script du système de surveillance..."

if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 n'est pas installé. Installation..."
    sudo apt update && sudo apt install -y python3 python3-pip python3-venv
fi

if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

echo "🎯 Activation de l'environnement virtuel..."
source venv/bin/activate

echo "📦 Installation des dépendances..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "❌ Fichier requirements.txt non trouvé!"
    exit 1
fi

echo "📁 Création des dossiers..."
mkdir -p logs

python main.py