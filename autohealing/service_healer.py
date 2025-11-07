import subprocess
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class ServiceHealer:
    def __init__(self, max_restart_attempts=3):
        self.max_restart_attempts = max_restart_attempts
        self.restart_attempts = {}  # Pour suivre les tentatives par service
        self.successful_restarts = 0
        self.failed_restarts = 0
    
    def restart_service(self, service_name):
        """Tente de redémarrer un service automatiquement"""
        try:
            # Vérifier si on n'a pas dépassé le nombre maximum de tentatives
            current_attempts = self.restart_attempts.get(service_name, 0)
            if current_attempts >= self.max_restart_attempts:
                logger.error(f"❌ Trop de tentatives de redémarrage pour {service_name} ({current_attempts}/{self.max_restart_attempts})")
                self.failed_restarts += 1
                return False, "Maximum de tentatives atteint"
            
            logger.info(f"🔄 Tentative de redémarrage du service {service_name} ({current_attempts + 1}/{self.max_restart_attempts})")
            
            # Tenter de redémarrer le service
            result = subprocess.run(
                ['sudo', 'systemctl', 'restart', service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Vérifier que le service est bien démarré
                import time
                time.sleep(2)  # Attendre un peu que le service démarre
                
                status_result = subprocess.run(
                    ['systemctl', 'is-active', service_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if status_result.returncode == 0:
                    logger.info(f"✅ Service {service_name} redémarré avec succès")
                    self.restart_attempts[service_name] = 0  # Réinitialiser le compteur
                    self.successful_restarts += 1
                    
                    # Log détaillé
                    action_details = {
                        'service': service_name,
                        'action': 'restart_service',
                        'status': 'success',
                        'attempt_number': current_attempts + 1,
                        'timestamp': datetime.now().isoformat()
                    }
                    return True, "Service redémarré avec succès", action_details
                else:
                    logger.warning(f"⚠️ Service {service_name} redémarré mais toujours inactif")
                    self.restart_attempts[service_name] = current_attempts + 1
                    self.failed_restarts += 1
                    
                    action_details = {
                        'service': service_name,
                        'action': 'restart_service',
                        'status': 'partial_success',
                        'attempt_number': current_attempts + 1,
                        'message': 'Service redémarré mais toujours inactif',
                        'timestamp': datetime.now().isoformat()
                    }
                    return False, "Service redémarré mais toujours inactif", action_details
            else:
                logger.error(f"❌ Échec du redémarrage de {service_name}: {result.stderr}")
                self.restart_attempts[service_name] = current_attempts + 1
                self.failed_restarts += 1
                
                action_details = {
                    'service': service_name,
                    'action': 'restart_service',
                    'status': 'failed',
                    'attempt_number': current_attempts + 1,
                    'error': result.stderr,
                    'timestamp': datetime.now().isoformat()
                }
                return False, f"Échec du redémarrage: {result.stderr}", action_details
                
        except subprocess.TimeoutExpired:
            error_msg = f"Timeout lors du redémarrage de {service_name}"
            logger.error(error_msg)
            self.restart_attempts[service_name] = current_attempts + 1
            self.failed_restarts += 1
            
            action_details = {
                'service': service_name,
                'action': 'restart_service',
                'status': 'failed',
                'attempt_number': current_attempts + 1,
                'error': 'Timeout',
                'timestamp': datetime.now().isoformat()
            }
            return False, error_msg, action_details
            
        except Exception as e:
            error_msg = f"Erreur lors du redémarrage de {service_name}: {e}"
            logger.error(error_msg)
            self.restart_attempts[service_name] = current_attempts + 1
            self.failed_restarts += 1
            
            action_details = {
                'service': service_name,
                'action': 'restart_service',
                'status': 'failed',
                'attempt_number': current_attempts + 1,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False, error_msg, action_details
    
    # def get_service_status(self, service_name):
    #     """Vérifie le statut d'un service"""
    #     try:
    #         result = subprocess.run(
    #             ['systemctl', 'is-active', service_name],
    #             capture_output=True,
    #             text=True,
    #             timeout=10
    #         )
    #         return result.returncode == 0
    #     except Exception as e:
    #         logger.error(f"Erreur lors de la vérification du service {service_name}: {e}")
    #         return False
    
    def get_healing_stats(self):
        """Retourne les statistiques de réparation"""
        return {
            'successful_restarts': self.successful_restarts,
            'failed_restarts': self.failed_restarts,
            'restart_attempts': self.restart_attempts,
            'max_restart_attempts': self.max_restart_attempts
        }
    
    # def reset_attempts(self, service_name=None):
    #     """Réinitialise les compteurs de tentatives"""
    #     if service_name:
    #         if service_name in self.restart_attempts:
    #             del self.restart_attempts[service_name]
    #     else:
    #         self.restart_attempts.clear()