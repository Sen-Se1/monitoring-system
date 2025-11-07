#!/usr/bin/env python3
"""
Tableau de bord autonome - À exécuter séparément si besoin
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard import MonitoringDashboard

if __name__ == "__main__":
    print("📊 Lancement du tableau de bord autonome...")
    print("💡 Tableau de bord disponible sur: http://localhost:8050")
    dashboard = MonitoringDashboard(port=8050)
    dashboard.run_dashboard()