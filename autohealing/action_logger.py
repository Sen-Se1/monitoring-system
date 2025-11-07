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
        
        # Écrire l'en-tête si le fichier est nouveau
        if not os.path.exists(log_file) or os.path.getsize(log_file) == 0:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("# timestamp - action_type - status - message\n")
        
        # Configuration du logger d'actions
        self.logger = logging.getLogger('action_logger')
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        
        # Éviter les handlers dupliqués
        if not self.logger.handlers:
            handler = logging.FileHandler(log_file, encoding='utf-8')
            # Format personnalisé : timestamp - action_type - status - message
            formatter = logging.Formatter('%(asctime)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def log_action(self, action_type, status, details=None, message=""):
        """Enregistre une action d'auto-réparation"""
        if not self.enabled:
            return
        
        # Formater le message dans le format: action_type - status - message
        formatted_message = f"{action_type} - {status} - {message}"
        
        # Logger avec le format personnalisé
        self.logger.info(formatted_message)
        
        # Log console séparé avec emojis
        status_icon = "✅" if status == "success" else "❌" if status == "failed" else "⚠️"
        print(f"   {status_icon} {action_type}: {message}")
    
    def log_service_restart(self, service_name, success, message, details=None):
        """Enregistre spécifiquement un redémarrage de service"""
        status = "success" if success else "failed"
        self.log_action(
            action_type=f"service_restart.{service_name}",
            status=status,
            details=details,
            message=message
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