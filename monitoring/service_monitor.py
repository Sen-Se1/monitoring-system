import subprocess
import logging

logger = logging.getLogger(__name__)

class ServiceMonitor:
    def __init__(self, services_to_monitor):
        self.services = services_to_monitor
    
    def check_service(self, service_name):
        """Vérifie l'état d'un service systemd"""
        try:
            result = subprocess.run(
                ['systemctl', 'is-active', service_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout lors de la vérification du service {service_name}")
            return False
        except Exception as e:
            logger.error(f"Erreur avec le service {service_name}: {e}")
            return False
    
    def check_all_services(self):
        """Vérifie tous les services configurés"""
        results = {}
        for service in self.services:
            results[service] = self.check_service(service)
        return results
    
    # def get_service_details(self, service_name):
    #     """Récupère des détails supplémentaires sur un service"""
    #     try:
    #         # Statut détaillé
    #         result = subprocess.run(
    #             ['systemctl', 'show', service_name, '--property=ActiveState,SubState,MainPID'],
    #             capture_output=True,
    #             text=True,
    #             timeout=5
    #         )
    #         details = {}
    #         for line in result.stdout.strip().split('\n'):
    #             if '=' in line:
    #                 key, value = line.split('=', 1)
    #                 details[key] = value
    #         return details
    #     except Exception as e:
    #         logger.error(f"Erreur lors de la récupération des détails pour {service_name}: {e}")
    #         return {}