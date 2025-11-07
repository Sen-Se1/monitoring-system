import subprocess

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
            return False
        except Exception as e:
            return False
    
    def check_all_services(self):
        """Vérifie tous les services configurés"""
        results = {}
        for service in self.services:
            results[service] = self.check_service(service)
        return results