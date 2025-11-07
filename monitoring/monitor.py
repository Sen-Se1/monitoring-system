import time
import platform
from config.settings import (
    MONITORING_INTERVAL, CPU_THRESHOLD, MEMORY_THRESHOLD, 
    DISK_THRESHOLD, NETWORK_THRESHOLD, MONITORED_SERVICES, 
    LOG_FILE, 
    AUTO_HEALING_ENABLED, CLEANUP_PATHS
)
from monitoring.system_monitor import SystemMonitor
from monitoring.service_monitor import ServiceMonitor
from monitoring.alert_manager import AlertManager
from autohealing.service_healer import ServiceHealer
from autohealing.system_healer import SystemHealer
from autohealing.action_logger import ActionLogger
from autohealing.triggers import AutoHealingTriggers
from utils.json_array_logger import JSONArrayLogger

# Initialisation du logger JSON array
json_logger = JSONArrayLogger(LOG_FILE)

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

def log_metrics_to_json(metrics, json_logger):
    """Log les métriques en JSON (sans affichage console)"""
    json_logger.log_metric('system', {
        'cpu_percent': metrics['cpu'],
        'memory_percent': metrics['memory'],
        'disk_percent': metrics['disk'],
        'network_sent_mb': metrics['network']['sent_mb'],
        'network_recv_mb': metrics['network']['recv_mb'],
        'total_network_mb': metrics['network']['sent_mb'] + metrics['network']['recv_mb']
    }, {
        'timestamp': metrics['timestamp']
    })

def log_alerts_to_json(alerts, json_logger):
    """Log les alertes en JSON (sans affichage console)"""
    for alert in alerts:
        json_logger.log_alert(
            alert_type=alert['type'],
            severity=alert['severity'],
            message=alert['message'],
            details={
                'value': alert.get('value'),
                'threshold': alert.get('threshold'),
                'service': alert.get('service')
            }
        )

def log_services_to_json(services_status, json_logger):
    """Log le statut des services en JSON (sans affichage console)"""
    for service, status in services_status.items():
        json_logger.log_metric('service_status', {
            'service': service,
            'status': 'active' if status else 'inactive'
        })

def main():
    """Fonction principale de surveillance"""
    print("🚀 Démarrage du système de surveillance...")
    json_logger.log_system_event('start', "Démarrage du système de surveillance")
    
    # Initialisation des modules de surveillance
    system_monitor = SystemMonitor()
    service_monitor = ServiceMonitor(MONITORED_SERVICES)
    alert_manager = AlertManager(CPU_THRESHOLD, MEMORY_THRESHOLD, DISK_THRESHOLD, NETWORK_THRESHOLD)
    
    # Initialisation des modules d'auto-réparation
    action_logger = ActionLogger(enabled=True, json_logger=json_logger)
    service_healer = ServiceHealer(action_logger=action_logger)  # Plus de max_restart_attempts
    system_healer = SystemHealer(cleanup_paths=CLEANUP_PATHS)
    healing_triggers = AutoHealingTriggers(service_healer, system_healer, action_logger)
    
    display_system_info(AUTO_HEALING_ENABLED)
    print("=" * 60)
    
    cycle_count = 0
    
    try:
        while True:
            cycle_count += 1
            print(f"\n🔄 Cycle de surveillance #{cycle_count}")
            json_logger.log_system_event('monitoring_cycle', f"Cycle de surveillance #{cycle_count}")
            
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
            
            # Log en JSON (sans affichage console)
            log_metrics_to_json(metrics, json_logger)
            log_services_to_json(services_status, json_logger)
            log_alerts_to_json(all_alerts, json_logger)
            
            # Affichage des résultats (SEULEMENT ICI pour éviter les doublons)
            display_system_metrics(metrics)
            display_services_status(services_status)
            
            # Gestion des alertes
            alerts_display = alert_manager.format_alerts_for_display(all_alerts)
            print(alerts_display)
            
            # Affichage des actions d'auto-réparation
            if healing_actions:
                healing_display = display_healing_actions(healing_actions)
                print(healing_display)
            
            print("-" * 60)
            
            # Affichage des statistiques occasionnellement
            if cycle_count % 10 == 0:
                stats = healing_triggers.get_healing_status()
                stats_msg = f"Statistiques auto-réparation: {stats['service_stats']['successful_restarts']} services redémarrés, {stats['system_stats']['cleanup_actions']} nettoyages effectués"
                json_logger.log_system_event('statistics', stats_msg)
                print(f"📈 {stats_msg}")
            
            # Attente avant le prochain check
            time.sleep(MONITORING_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du système de surveillance")
        json_logger.log_system_event('shutdown', "Arrêt du système de surveillance")
        
        # Afficher les statistiques finales
        if AUTO_HEALING_ENABLED:
            stats = healing_triggers.get_healing_status()
            print(f"\n📊 Statistiques finales auto-réparation:")
            print(f"   Services redémarrés: {stats['service_stats']['successful_restarts']}")
            print(f"   Nettoyages disque: {stats['system_stats']['cleanup_actions']}")
            print(f"   Caches vidés: {stats['system_stats']['cache_clears']}")
            print(f"   Processus terminés: {stats['system_stats']['process_kills']}")
        
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        json_logger.log_system_event('error', f"Erreur critique: {e}")

if __name__ == "__main__":
    main()