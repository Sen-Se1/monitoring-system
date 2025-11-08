from config.settings import EMAIL_ALERTS_ENABLED, EMAIL_RECIPIENTS, EMAIL_ALERT_INTERVAL

class AlertManager:
    def __init__(self, cpu_threshold, memory_threshold, disk_threshold, network_threshold, email_sender=None):
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
        self.network_threshold = network_threshold
        self.email_sender = email_sender
        self.sent_alerts = set()
    
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
                'message': f"🚨 {severity} - CPU élevé: {cpu_value}% (seuil: {self.cpu_threshold}%)"
            }
            alerts.append(alert_data)
            
            # Envoyer email si critique
            if severity == "CRITIQUE":
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
                'message': f"🚨 {severity} - Mémoire élevée: {memory_value}% (seuil: {self.memory_threshold}%)"
            }
            alerts.append(alert_data)
            
            # Envoyer email si critique
            if severity == "CRITIQUE":
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
                'message': f"🚨 {severity} - Espace disque faible: {disk_value}% (seuil: {self.disk_threshold}%)"
            }
            alerts.append(alert_data)
            
            # Envoyer email si critique
            if severity == "CRITIQUE":
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
                'message': f"🚨 {severity} - Utilisation réseau élevée: {total_network_mb:.1f}MB (seuil: {self.network_threshold}MB)"
            }
            alerts.append(alert_data)
            
            # Envoyer email si critique
            if severity == "CRITIQUE":
                self._send_email_alert(alert_data)
        
        return alerts
    
    def check_services_alerts(self, services_status):
        """Vérifie les services arrêtés (sans auto-réparation)"""
        alerts = []
        for service, status in services_status.items():
            if not status:
                alert_data = {
                    'type': 'service_down',
                    'service': service,
                    'severity': 'CRITIQUE',
                    'message': f"🔴 Service {service} est arrêté"
                }
                alerts.append(alert_data)
                
                # Toujours envoyer email pour les services arrêtés
                self._send_email_alert(alert_data)
        return alerts
    
    def _send_email_alert(self, alert_data):
        print("alert_data:", alert_data)
        """Envoie une alerte par email si configuré"""
        if not EMAIL_ALERTS_ENABLED or not self.email_sender or not EMAIL_RECIPIENTS:
            return
        
        # Créer une clé unique pour cette alerte (pour éviter les doublons)
        alert_key = f"{alert_data['type']}_{alert_data.get('service', '')}_{alert_data.get('value', '')}"
        
        # Vérifier si on peut envoyer cette alerte (anti-spam)
        if self.email_sender.can_send_alert(alert_key, EMAIL_ALERT_INTERVAL):
            subject = f"Alerte {alert_data['severity']} - {alert_data['type'].replace('_', ' ').title()}"
            message = f"""
            Une alerte {alert_data['severity']} a été détectée sur le système.
            
            Détails:
            {alert_data['message']}
            
            Type: {alert_data['type']}
            Service: {alert_data.get('service', 'Système')}
            Valeur: {alert_data.get('value', 'N/A')}
            Seuil: {alert_data.get('threshold', 'N/A')}
            
            Heure de détection: {alert_data.get('timestamp', 'Inconnue')}
            
            Veuillez vérifier le système dès que possible.
            """
            
            self.email_sender.send_alert_email(EMAIL_RECIPIENTS, subject, message, alert_key)
    
    def format_alerts_for_display(self, alerts):
        """Formate les alertes pour l'affichage (avec emojis)"""
        if not alerts:
            return "✅ Tous les systèmes sont normaux"
        
        output = "🚨 ALERTES:\n"
        for alert in alerts:
            output += f"   {alert['message']}\n"
        return output.strip()