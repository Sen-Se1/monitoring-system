import logging
import json
from datetime import datetime
import os

class ActionLogger:
    def __init__(self, log_file="logs/actions.log", enabled=True):
        self.log_file = log_file
        self.enabled = enabled
        
        # Créer le dossier logs si nécessaire
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Configuration du logger d'actions
        self.logger = logging.getLogger('action_logger')
        self.logger.setLevel(logging.INFO)
        
        # Éviter les handlers dupliqués
        if not self.logger.handlers:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter('%(asctime)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_action(self, action_type, status, details=None, message=""):
        """Enregistre une action d'auto-réparation"""
        if not self.enabled:
            return
        
        action_record = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'status': status,
            'message': message,
            'details': details or {}
        }
        
        # Log structuré en JSON
        self.logger.info(json.dumps(action_record))
        
        # Also log to console for immediate feedback
        status_icon = "✅" if status == "success" else "❌" if status == "failed" else "⚠️"
        print(f"   {status_icon} {action_type}: {message}")
    
    def log_service_restart(self, service_name, success, message, details=None):
        """Enregistre spécifiquement un redémarrage de service"""
        status = "success" if success else "failed"
        self.log_action(
            action_type="service_restart",
            status=status,
            details=details,
            message=f"Service {service_name} - {message}"
        )
    
    def log_system_healing(self, action_type, success, message, details=None):
        """Enregistre spécifiquement une action de réparation système"""
        status = "success" if success else "failed"
        self.log_action(
            action_type=action_type,
            status=status,
            details=details,
            message=message
        )
    
    # def get_recent_actions(self, limit=50):
    #     """Récupère les actions récentes depuis le fichier de log"""
    #     try:
    #         with open(self.log_file, 'r') as f:
    #             lines = f.readlines()[-limit:]
    #             actions = [json.loads(line.split(' - ', 1)[1]) for line in lines]
    #             return actions
    #     except (FileNotFoundError, json.JSONDecodeError):
    #         return []