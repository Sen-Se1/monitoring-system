import logging
from config.settings import (
    AUTO_HEAL_CPU_THRESHOLD, AUTO_HEAL_MEMORY_THRESHOLD, 
    AUTO_HEAL_DISK_THRESHOLD, AUTO_HEALING_ENABLED
)

logger = logging.getLogger(__name__)

class AutoHealingTriggers:
    def __init__(self, service_healer, system_healer, action_logger):
        self.service_healer = service_healer
        self.system_healer = system_healer
        self.action_logger = action_logger
        self.enabled = AUTO_HEALING_ENABLED
    
    def evaluate_and_heal(self, metrics, services_status):
        """Évalue les métriques et déclenche l'auto-réparation si nécessaire"""
        healing_actions = []
        
        if not self.enabled:
            return healing_actions
        
        # Réparation des services arrêtés
        service_actions = self._heal_stopped_services(services_status)
        healing_actions.extend(service_actions)
        
        # Réparation système basée sur les métriques
        system_actions = self._heal_system_issues(metrics)
        healing_actions.extend(system_actions)
        
        return healing_actions
    
    def _heal_stopped_services(self, services_status):
        """Réparation automatique des services arrêtés"""
        healing_actions = []
        
        for service, status in services_status.items():
            if not status:  # Service arrêté
                logger.warning(f"🔴 Service {service} arrêté - Tentative de redémarrage automatique")
                
                success, message, details = self.service_healer.restart_service(service)
                
                healing_actions.append({
                    'type': 'service_restart',
                    'service': service,
                    'success': success,
                    'message': message,
                    'details': details
                })
                
                # Log de l'action
                self.action_logger.log_service_restart(service, success, message, details)
        
        return healing_actions
    
    def _heal_system_issues(self, metrics):
        """Réparation automatique des problèmes système"""
        healing_actions = []
        
        cpu_value = metrics['cpu']
        memory_value = metrics['memory']
        disk_value = metrics['disk']
        
        # CPU trop élevé
        if cpu_value > AUTO_HEAL_CPU_THRESHOLD:
            logger.warning(f"🔥 CPU élevé ({cpu_value}%) - Nettoyage des caches")
            
            success, message, details = self.system_healer.clear_cache()
            
            healing_actions.append({
                'type': 'clear_cache',
                'trigger': 'high_cpu',
                'success': success,
                'message': message,
                'details': details
            })
            
            self.action_logger.log_system_healing('clear_cache', success, message, details)
        
        # Mémoire trop élevée
        if memory_value > AUTO_HEAL_MEMORY_THRESHOLD:
            logger.warning(f"💾 Mémoire élevée ({memory_value}%) - Recherche de processus gourmands")
            
            success, message, details = self.system_healer.kill_process_by_memory(threshold_percent=15.0)
            
            healing_actions.append({
                'type': 'kill_process',
                'trigger': 'high_memory',
                'success': success,
                'message': message,
                'details': details
            })
            
            self.action_logger.log_system_healing('kill_process', success, message, details)
        
        # Disque presque plein
        if disk_value > AUTO_HEAL_DISK_THRESHOLD:
            logger.warning(f"💽 Disque presque plein ({disk_value}%) - Nettoyage des fichiers temporaires")
            
            success, message, details = self.system_healer.cleanup_temp_files()
            
            healing_actions.append({
                'type': 'cleanup_temp_files',
                'trigger': 'low_disk',
                'success': success,
                'message': message,
                'details': details
            })
            
            self.action_logger.log_system_healing('cleanup_temp_files', success, message, details)
        
        return healing_actions
    
    # def enable_auto_healing(self):
    #     """Active l'auto-réparation"""
    #     self.enabled = True
    #     logger.info("✅ Auto-réparation activée")
    
    # def disable_auto_healing(self):
    #     """Désactive l'auto-réparation"""
    #     self.enabled = False
    #     logger.info("❌ Auto-réparation désactivée")
    
    def get_healing_status(self):
        """Retourne le statut de l'auto-réparation"""
        return {
            'enabled': self.enabled,
            'service_stats': self.service_healer.get_healing_stats(),
            'system_stats': self.system_healer.get_healing_stats()
        }