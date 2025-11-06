#!/usr/bin/env python3
"""
Script principal de surveillance système et services
"""

import time
import logging
from config.settings import MONITORING_INTERVAL, CPU_THRESHOLD, MEMORY_THRESHOLD, DISK_THRESHOLD, MONITORED_SERVICES, LOG_FILE, LOG_LEVEL
from monitoring.system_monitor import SystemMonitor
from monitoring.service_monitor import ServiceMonitor
from monitoring.alert_manager import AlertManager

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def display_system_metrics(metrics):
    """Affiche les métriques système"""
    print(f"📊 [{metrics['timestamp']}] Métriques système:")
    print(f"   CPU: {metrics['cpu']:.1f}% | Mémoire: {metrics['memory']:.1f}% | Disque: {metrics['disk']:.1f}%")
    print(f"   Réseau: ↑{metrics['network']['sent_mb']:.1f}MB ↓{metrics['network']['recv_mb']:.1f}MB")

def display_services_status(services_status):
    """Affiche le statut des services"""
    print("🔧 État des services:")
    for service, status in services_status.items():
        status_icon = "🟢" if status else "🔴"
        status_text = "Actif" if status else "Arrêté"
        print(f"   {status_icon} {service}: {status_text}")

def log_alerts(alerts):
    """Log les alertes dans le fichier"""
    for alert in alerts:
        logger.warning(f"{alert['type']} - {alert['message']}")

def main():
    """Fonction principale de surveillance"""
    print("🚀 Démarrage du système de surveillance...")
    print(f"⏰ Intervalle: {MONITORING_INTERVAL} secondes")
    print(f"📊 Seuils - CPU: {CPU_THRESHOLD}%, Mémoire: {MEMORY_THRESHOLD}%, Disque: {DISK_THRESHOLD}%")
    print(f"🔧 Services surveillés: {', '.join(MONITORED_SERVICES)}")
    print("=" * 60)
    
    # Initialisation des modules
    system_monitor = SystemMonitor()
    service_monitor = ServiceMonitor(MONITORED_SERVICES)
    alert_manager = AlertManager(CPU_THRESHOLD, MEMORY_THRESHOLD, DISK_THRESHOLD)
    
    cycle_count = 0
    
    try:
        while True:
            cycle_count += 1
            print(f"\n🔄 Cycle de surveillance #{cycle_count}")
            
            # Récupération des métriques
            metrics = system_monitor.check_all_metrics()
            services_status = service_monitor.check_all_services()
            
            # Vérification des alertes
            system_alerts = alert_manager.check_thresholds(metrics)
            service_alerts = alert_manager.check_services_alerts(services_status)
            all_alerts = system_alerts + service_alerts
            
            # Affichage des résultats
            display_system_metrics(metrics)
            display_services_status(services_status)
            
            # Gestion des alertes
            alerts_display = alert_manager.format_alerts_for_display(all_alerts)
            print(alerts_display)
            
            # Log des alertes
            log_alerts(all_alerts)
            
            print("-" * 60)
            
            # Attente avant le prochain check
            time.sleep(MONITORING_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du système de surveillance")
        logger.info("Arrêt du système de surveillance")
    except Exception as e:
        error_msg = f"Erreur critique: {e}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")

if __name__ == "__main__":
    main()