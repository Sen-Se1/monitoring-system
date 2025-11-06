import logging

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self, cpu_threshold, memory_threshold, disk_threshold, network_threshold):
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
        self.network_threshold = network_threshold
    
    def check_thresholds(self, metrics):
        """Vérifie si les métriques dépassent les seuils"""
        alerts = []
        
        # Vérification CPU
        cpu_value = metrics['cpu']
        if cpu_value > self.cpu_threshold:
            severity = "CRITIQUE" if cpu_value > 90 else "AVERTISSEMENT"
            alerts.append({
                'type': 'high_cpu',
                'value': cpu_value,
                'threshold': self.cpu_threshold,
                'severity': severity,
                'message': f"🚨 {severity} - CPU élevé: {cpu_value}% (seuil: {self.cpu_threshold}%)"
            })
        
        # Vérification Mémoire
        memory_value = metrics['memory']
        if memory_value > self.memory_threshold:
            severity = "CRITIQUE" if memory_value > 95 else "AVERTISSEMENT"
            alerts.append({
                'type': 'high_memory',
                'value': memory_value,
                'threshold': self.memory_threshold,
                'severity': severity,
                'message': f"🚨 {severity} - Mémoire élevée: {memory_value}% (seuil: {self.memory_threshold}%)"
            })
        
        # Vérification Disque
        disk_value = metrics['disk']
        if disk_value > self.disk_threshold:
            severity = "CRITIQUE" if disk_value > 95 else "AVERTISSEMENT"
            alerts.append({
                'type': 'low_disk',
                'value': disk_value,
                'threshold': self.disk_threshold,
                'severity': severity,
                'message': f"🚨 {severity} - Espace disque faible: {disk_value}% (seuil: {self.disk_threshold}%)"
            })
        
        # Vérification Réseau
        network_data = metrics['network']
        total_network_mb = network_data['sent_mb'] + network_data['recv_mb']
        if total_network_mb > self.network_threshold:
            severity = "CRITIQUE" if total_network_mb > (self.network_threshold * 2) else "AVERTISSEMENT"
            alerts.append({
                'type': 'high_network',
                'value': total_network_mb,
                'threshold': self.network_threshold,
                'severity': severity,
                'message': f"🚨 {severity} - Utilisation réseau élevée: {total_network_mb:.1f}MB (seuil: {self.network_threshold}MB)"
            })
        
        return alerts
    
    def check_services_alerts(self, services_status):
        """Vérifie les services arrêtés"""
        alerts = []
        for service, status in services_status.items():
            if not status:
                alerts.append({
                    'type': 'service_down',
                    'service': service,
                    'severity': 'CRITIQUE',
                    'message': f"🔴 Service {service} est arrêté"
                })
        return alerts
    
    def format_alerts_for_display(self, alerts):
        """Formate les alertes pour l'affichage"""
        if not alerts:
            return "✅ Tous les systèmes sont normaux"
        
        output = "🚨 ALERTES:\n"
        for alert in alerts:
            output += f"   {alert['message']}\n"
        return output.strip()