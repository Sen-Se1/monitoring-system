from config.settings import EMAIL_ALERTS_ENABLED, EMAIL_RECIPIENTS, EMAIL_ALERT_INTERVAL
from datetime import datetime

class AlertManager:
    def __init__(self, cpu_threshold, memory_threshold, disk_threshold, network_threshold, email_sender=None):
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
        self.network_threshold = network_threshold
        self.email_sender = email_sender
        self.sent_alerts = set()  # Pour éviter les doublons
    
    def check_thresholds(self, metrics):
        """Vérifie si les métriques dépassent les seuils (sans auto-réparation)"""
        alerts = []
        
        # Vérification CPU
        cpu_value = metrics['cpu']
        if cpu_value > self.cpu_threshold:
            severity = "CRITIQUE" if cpu_value > 90 else "AVERTISSEMENT"
            alert_data = {
                'type': 'high_cpu',
                'value': cpu_value,
                'threshold': self.cpu_threshold,
                'severity': severity,
                'message': f"🚨 {severity} - CPU élevé: {cpu_value}% (seuil: {self.cpu_threshold}%)",
                'timestamp': metrics['timestamp']
            }
            alerts.append(alert_data)
            
            # Envoyer email pour TOUTES les alertes CPU (pas seulement critiques)
            self._send_email_alert(alert_data)
        
        # Vérification Mémoire
        memory_value = metrics['memory']
        if memory_value > self.memory_threshold:
            severity = "CRITIQUE" if memory_value > 95 else "AVERTISSEMENT"
            alert_data = {
                'type': 'high_memory',
                'value': memory_value,
                'threshold': self.memory_threshold,
                'severity': severity,
                'message': f"🚨 {severity} - Mémoire élevée: {memory_value}% (seuil: {self.memory_threshold}%)",
                'timestamp': metrics['timestamp']
            }
            alerts.append(alert_data)
            
            # Envoyer email pour TOUTES les alertes mémoire (pas seulement critiques)
            self._send_email_alert(alert_data)
        
        # Vérification Disque
        disk_value = metrics['disk']
        if disk_value > self.disk_threshold:
            severity = "CRITIQUE" if disk_value > 95 else "AVERTISSEMENT"
            alert_data = {
                'type': 'low_disk',
                'value': disk_value,
                'threshold': self.disk_threshold,
                'severity': severity,
                'message': f"🚨 {severity} - Espace disque faible: {disk_value}% (seuil: {self.disk_threshold}%)",
                'timestamp': metrics['timestamp']
            }
            alerts.append(alert_data)
            
            # Envoyer email pour TOUTES les alertes disque (pas seulement critiques)
            self._send_email_alert(alert_data)
        
        # Vérification Réseau
        network_data = metrics['network']
        total_network_mb = network_data['sent_mb'] + network_data['recv_mb']
        if total_network_mb > self.network_threshold:
            severity = "CRITIQUE" if total_network_mb > (self.network_threshold * 2) else "AVERTISSEMENT"
            alert_data = {
                'type': 'high_network',
                'value': total_network_mb,
                'threshold': self.network_threshold,
                'severity': severity,
                'message': f"🚨 {severity} - Utilisation réseau élevée: {total_network_mb:.1f}MB (seuil: {self.network_threshold}MB)",
                'timestamp': metrics['timestamp']
            }
            alerts.append(alert_data)
            
            # Envoyer email pour TOUTES les alertes réseau (pas seulement critiques)
            self._send_email_alert(alert_data)
        
        return alerts
    
    def check_services_alerts(self, services_status):
        """Vérifie les services arrêtés (sans auto-réparation)"""
        alerts = []
        current_time = datetime.now().isoformat()  # Changé pour format ISO comme les logs JSON
        for service, status in services_status.items():
            if not status:
                alert_data = {
                    'type': 'service_down',
                    'service': service,
                    'severity': 'CRITIQUE',
                    'message': f"🔴 Service {service} est arrêté",
                    'timestamp': current_time
                }
                alerts.append(alert_data)
                
                # Toujours envoyer email pour les services arrêtés
                self._send_email_alert(alert_data)
        return alerts
    
    def _send_email_alert(self, alert_data):
        """Envoie une alerte par email si configuré"""
        if not EMAIL_ALERTS_ENABLED or not self.email_sender or not EMAIL_RECIPIENTS:
            return
        
        # Créer une clé unique pour cette alerte (pour éviter les doublons)
        alert_key = f"{alert_data['type']}_{alert_data.get('service', '')}"
        
        # Vérifier si on peut envoyer cette alerte (anti-spam)
        if self.email_sender.can_send_alert(alert_key, EMAIL_ALERT_INTERVAL):
            subject = f"Alerte {alert_data['severity']} - {self._get_alert_type_display(alert_data['type'])}"
            message = self._create_email_message(alert_data)
            
            self.email_sender.send_alert_email(EMAIL_RECIPIENTS, subject, message, alert_key)
    
    def _get_alert_type_display(self, alert_type):
        """Retourne le nom d'affichage pour le type d'alerte"""
        types = {
            'high_cpu': 'CPU Élevé',
            'high_memory': 'Mémoire Élevée',
            'low_disk': 'Espace Disque Faible',
            'high_network': 'Réseau Élevé',
            'service_down': 'Service Arrêté'
        }
        return types.get(alert_type, alert_type.replace('_', ' ').title())
    
    def _format_timestamp_for_email(self, timestamp):
        """Formate le timestamp ISO pour l'email (plus lisible)"""
        try:
            # Si c'est déjà au format lisible, on le garde
            if 'T' in timestamp:
                # Format ISO: "2025-11-08T01:28:26.887473" → "2025-11-08 01:28:26"
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # Déjà au bon format
                return timestamp
        except (ValueError, TypeError):
            # En cas d'erreur, retourner le timestamp original
            return timestamp
    
    def _create_email_message(self, alert_data):
        """Crée le message email en fonction du type d'alerte"""
        # Utiliser le timestamp de l'alerte (celui des logs JSON)
        detection_time = self._format_timestamp_for_email(alert_data.get('timestamp', ''))
        
        if alert_data['type'] == 'service_down':
            return f"""
                Un service critique a été détecté comme arrêté.

                DÉTAILS:
                • Service: {alert_data['service']}
                • Statut: Arrêté
                • Sévérité: {alert_data['severity']}
                • Heure de détection: {detection_time}

                ACTION REQUISE:
                Veuillez redémarrer le service manuellement ou vérifier sa configuration.
            """
        else:
            return f"""
                Une alerte a été détectée sur le système.

                DÉTAILS:
                • Type: {self._get_alert_type_display(alert_data['type'])}
                • Sévérité: {alert_data['severity']}
                • Valeur actuelle: {alert_data.get('value', 'N/A')}
                • Seuil critique: {alert_data.get('threshold', 'N/A')}
                • Heure de détection: {detection_time}
            """
    
    def format_alerts_for_display(self, alerts):
        """Formate les alertes pour l'affichage (avec emojis)"""
        if not alerts:
            return "✅ Tous les systèmes sont normaux"
        
        output = "🚨 ALERTES:\n"
        for alert in alerts:
            output += f"   {alert['message']}\n"
        return output.strip()