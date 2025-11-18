import json
import os
import re
from datetime import datetime
from threading import Lock

class JSONArrayLogger:
    """Logger simple pour tableau JSON avec verrouillage"""
    
    def __init__(self, log_file="logs/monitoring.json"):
        self.log_file = log_file
        self.lock = Lock()
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        if not os.path.exists(log_file) or os.path.getsize(log_file) == 0:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2, ensure_ascii=False)
    
    def _remove_emojis(self, text):
        """Supprime les emojis d'un texte"""
        if not isinstance(text, str):
            return text
        
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        return emoji_pattern.sub(r'', text)
    
    def _clean_log_data(self, log_data):
        """Nettoie les emojis des données de log"""
        if isinstance(log_data, dict):
            cleaned = {}
            for key, value in log_data.items():
                if key == 'message' and isinstance(value, str):
                    cleaned[key] = self._remove_emojis(value)
                else:
                    cleaned[key] = self._clean_log_data(value)
            return cleaned
        elif isinstance(log_data, list):
            return [self._clean_log_data(item) for item in log_data]
        else:
            return log_data
    
    def _append_log(self, log_data):
        """Ajoute une entrée au tableau JSON (sans emojis)"""
        cleaned_log_data = self._clean_log_data(log_data)
        
        with self.lock:
            try:
                if os.path.getsize(self.log_file) > 0:
                    with open(self.log_file, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                else:
                    logs = []
                
                logs.append(cleaned_log_data)
                
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, indent=2, ensure_ascii=False)
                    
            except json.JSONDecodeError:
                logs = [cleaned_log_data]
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Error writing to JSON log: {e}")
    
    def log_metric(self, metric_type, values, metadata=None):
        """Log une métrique système (SANS affichage console)"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'metric',
            'metric_type': metric_type,
            'values': values,
            'metadata': metadata or {}
        }
        self._append_log(log_data)
    
    def log_alert(self, alert_type, severity, message, details=None):
        """Log une alerte (SANS affichage console)"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'alert',
            'alert_type': alert_type,
            'severity': severity,
            'message': message,
            'details': details or {}
        }
        self._append_log(log_data)
    
    def log_action(self, action_type, status, service=None, message="", details=None):
        """Log une action d'auto-réparation (SANS affichage console)"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'action',
            'action_type': action_type,
            'status': status,
            'service': service,
            'message': message,
            'details': details or {}
        }
        self._append_log(log_data)
    
    def log_system_event(self, event_type, message, details=None):
        """Log un événement système (SANS affichage console)"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'event_type': 'system',
            'system_event_type': event_type,
            'message': message,
            'details': details or {}
        }
        self._append_log(log_data)