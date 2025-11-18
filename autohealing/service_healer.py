import subprocess
from datetime import datetime

class ServiceHealer:
    def __init__(self, action_logger=None):
        self.successful_restarts = 0
        self.failed_restarts = 0
        self.action_logger = action_logger
    
    def restart_service(self, service_name):
        """Tente de redémarrer un service automatiquement (toujours)"""
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', 'restart', service_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                import time
                time.sleep(2)
                
                status_result = subprocess.run(
                    ['systemctl', 'is-active', service_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if status_result.returncode == 0:
                    success_msg = f"Service {service_name} redémarré avec succès"
                    self.successful_restarts += 1
                    
                    action_details = {
                        'service': service_name,
                        'action': 'restart_service',
                        'status': 'success',
                        'timestamp': datetime.now().isoformat()
                    }
                    return True, success_msg, action_details
                else:
                    warning_msg = f"Service {service_name} redémarré mais toujours inactif"
                    self.failed_restarts += 1
                    
                    action_details = {
                        'service': service_name,
                        'action': 'restart_service',
                        'status': 'partial_success',
                        'message': 'Service redémarré mais toujours inactif',
                        'timestamp': datetime.now().isoformat()
                    }
                    return False, warning_msg, action_details
            else:
                error_msg = f"Échec du redémarrage de {service_name}: {result.stderr}"
                self.failed_restarts += 1
                
                action_details = {
                    'service': service_name,
                    'action': 'restart_service',
                    'status': 'failed',
                    'error': result.stderr,
                    'timestamp': datetime.now().isoformat()
                }
                return False, error_msg, action_details
                
        except subprocess.TimeoutExpired:
            error_msg = f"Timeout lors du redémarrage de {service_name}"
            self.failed_restarts += 1
            
            action_details = {
                'service': service_name,
                'action': 'restart_service',
                'status': 'failed',
                'error': 'Timeout',
                'timestamp': datetime.now().isoformat()
            }
            return False, error_msg, action_details
            
        except Exception as e:
            error_msg = f"Erreur lors du redémarrage de {service_name}: {e}"
            self.failed_restarts += 1
            
            action_details = {
                'service': service_name,
                'action': 'restart_service',
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False, error_msg, action_details
    
    def get_healing_stats(self):
        """Retourne les statistiques de réparation"""
        return {
            'successful_restarts': self.successful_restarts,
            'failed_restarts': self.failed_restarts
        }