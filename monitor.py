#!/usr/bin/env python3
"""
Script principal de surveillance système et services - Multi-plateforme
"""

import time
import logging
import platform
import os
from config.settings import (
    MONITORING_INTERVAL, CPU_THRESHOLD, MEMORY_THRESHOLD, 
    DISK_THRESHOLD, NETWORK_THRESHOLD, MONITORED_SERVICES, 
    LOG_FILE, LOG_LEVEL, 
    AUTO_HEALING_ENABLED, MAX_RESTART_ATTEMPTS, CLEANUP_PATHS,
    ACTION_LOG_FILE, LOG_ACTIONS_ENABLED
)
from monitoring.system_monitor import SystemMonitor
from monitoring.service_monitor import ServiceMonitor
from monitoring.alert_manager import AlertManager
from autohealing.service_healer import ServiceHealer
from autohealing.system_healer import SystemHealer
from autohealing.action_logger import ActionLogger
from autohealing.triggers import AutoHealingTriggers

# Créer le dossier logs si nécessaire
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Écrire l'en-tête si le fichier monitoring.log est nouveau
if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write("# timestamp - level - incident_type - message\n")

# Configuration du logging avec format personnalisé
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def display_system_info(auto_healing_enabled):
    """Affiche les informations du système"""
    system = platform.system()
    version = platform.version()
    print(f"💻 Système: {system} {version}")
    print(f"⏰ Intervalle: {MONITORING_INTERVAL} secondes")
    print(f"📊 Seuils - CPU: {CPU_THRESHOLD}%, Mémoire: {MEMORY_THRESHOLD}%, Disque: {DISK_THRESHOLD}%, Réseau: {NETWORK_THRESHOLD}MB")
    print(f"🔧 Services surveillés: {', '.join(MONITORED_SERVICES)}")
    print(f"⚡ Auto-réparation: {'ACTIVÉE' if auto_healing_enabled else 'DÉSACTIVÉE'}")

def display_system_metrics(metrics):
    """Affiche les métriques système"""
    print(f"📊 [{metrics['timestamp']}] Métriques système:")
    print(f"   CPU: {metrics['cpu']:.1f}% | Mémoire: {metrics['memory']:.1f}% | Disque: {metrics['disk']:.1f}%")
    network_data = metrics['network']
    total_network = network_data['sent_mb'] + network_data['recv_mb']
    print(f"   Réseau: ↑{network_data['sent_mb']:.1f}MB ↓{network_data['recv_mb']:.1f}MB (Total: {total_network:.1f}MB)")

def display_services_status(services_status):
    """Affiche le statut des services"""
    print("🔧 État des services:")
    for service, status in services_status.items():
        status_icon = "🟢" if status else "🔴"
        status_text = "Actif" if status else "Arrêté"
        print(f"   {status_icon} {service}: {status_text}")

def display_healing_actions(healing_actions):
    """Affiche les actions d'auto-réparation"""
    if not healing_actions:
        return ""
    
    output = "🔧 ACTIONS AUTO-RÉPARATION:\n"
    for action in healing_actions:
        icon = "✅" if action['success'] else "❌"
        action_type = action['type']
        message = action['message']
        output += f"   {icon} {action_type}: {message}\n"
    return output

def log_alerts(alerts):
    """Log les alertes dans le fichier avec le format personnalisé"""
    for alert in alerts:
        # Formater dans le format: incident_type - message
        formatted_message = f"{alert['type']} - {alert['message']}"
        
        if alert['severity'] == 'CRITIQUE':
            logger.error(formatted_message)
        else:
            logger.warning(formatted_message)

def main():
    """Fonction principale de surveillance"""
    print("🚀 Démarrage du système de surveillance...")
    
    # Initialisation des modules de surveillance
    system_monitor = SystemMonitor()
    service_monitor = ServiceMonitor(MONITORED_SERVICES)
    alert_manager = AlertManager(CPU_THRESHOLD, MEMORY_THRESHOLD, DISK_THRESHOLD, NETWORK_THRESHOLD)
    
    # Initialisation des modules d'auto-réparation
    service_healer = ServiceHealer(max_restart_attempts=MAX_RESTART_ATTEMPTS)
    system_healer = SystemHealer(cleanup_paths=CLEANUP_PATHS)
    action_logger = ActionLogger(log_file=ACTION_LOG_FILE, enabled=LOG_ACTIONS_ENABLED)
    healing_triggers = AutoHealingTriggers(service_healer, system_healer, action_logger)
    
    display_system_info(AUTO_HEALING_ENABLED)
    print("=" * 60)
    
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
            
            # Auto-réparation si activée
            healing_actions = []
            if AUTO_HEALING_ENABLED:
                healing_actions = healing_triggers.evaluate_and_heal(metrics, services_status)
            
            # Affichage des résultats
            display_system_metrics(metrics)
            display_services_status(services_status)
            
            # Gestion des alertes
            alerts_display = alert_manager.format_alerts_for_display(all_alerts)
            print(alerts_display)
            
            # Affichage des actions d'auto-réparation
            if healing_actions:
                healing_display = display_healing_actions(healing_actions)
                print(healing_display)
            
            # Log des alertes
            log_alerts(all_alerts)
            
            print("-" * 60)
            
            # Affichage des statistiques occasionnellement
            if cycle_count % 10 == 0:
                stats = healing_triggers.get_healing_status()
                print(f"📈 Statistiques auto-réparation: {stats['service_stats']['successful_restarts']} services redémarrés, "
                      f"{stats['system_stats']['cleanup_actions']} nettoyages effectués")
            
            # Attente avant le prochain check
            time.sleep(MONITORING_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du système de surveillance")
        
        # Afficher les statistiques finales
        if AUTO_HEALING_ENABLED:
            stats = healing_triggers.get_healing_status()
            print(f"\n📊 Statistiques finales auto-réparation:")
            print(f"   Services redémarrés: {stats['service_stats']['successful_restarts']}")
            print(f"   Nettoyages disque: {stats['system_stats']['cleanup_actions']}")
            print(f"   Caches vidés: {stats['system_stats']['cache_clears']}")
            print(f"   Processus terminés: {stats['system_stats']['process_kills']}")
        
        logger.info("Arrêt du système de surveillance")
    except Exception as e:
        error_msg = f"Erreur critique: {e}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")

if __name__ == "__main__":
    main()