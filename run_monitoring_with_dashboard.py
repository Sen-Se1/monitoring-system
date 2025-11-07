#!/usr/bin/env python3
"""
Script principal pour lancer la surveillance ET le tableau de bord
"""

import threading
import time
import os
import sys
from monitor import main as monitoring_main
from visualization.dashboard import MonitoringDashboard

def run_monitoring():
    """Lance le système de surveillance"""
    print("🔧 Démarrage du système de surveillance...")
    monitoring_main()

def run_dashboard():
    """Lance le tableau de bord"""
    print("📊 Démarrage du tableau de bord...")
    dashboard = MonitoringDashboard(port=8050)
    dashboard.run_dashboard()

def main():
    """Lance les deux systèmes en parallèle"""
    print("🚀 Démarrage du système de surveillance avec tableau de bord...")
    print("💡 Le tableau de bord sera disponible sur: http://localhost:8050")
    print("⏳ Démarrage dans 3 secondes...")
    time.sleep(3)
    
    # Créer les dossiers nécessaires
    os.makedirs("logs", exist_ok=True)
    os.makedirs("visualization", exist_ok=True)
    
    # Lancer le tableau de bord dans un thread séparé
    dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()
    
    # Lancer la surveillance dans le thread principal
    try:
        run_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du système complet...")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    main()