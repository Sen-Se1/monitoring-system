import logging
import json
from datetime import datetime
import os

class ActionLogger:
    def __init__(self, enabled=True):
        self.enabled = enabled
        # Utiliser le logger principal au lieu de créer un nouveau
        self.logger = logging.getLogger('monitoring')
    
    def log_action(self, action_type, status, details=None, message=""):
        """Enregistre une action d'auto-réparation dans le log principal"""
        if not self.enabled:
            return
        
        # Formater le message d'action de manière structurée
        formatted_message = f"ACTION - {action_type} - {status} - {message}"
        if details:
            formatted_message += f" | Details: {json.dumps(details)}"
        
        # Logger avec le niveau INFO pour les actions
        self.logger.info(formatted_message)
    
    def log_service_restart(self, service_name, success, message, details=None):
        """Enregistre spécifiquement un redémarrage de service"""
        status = "SUCCESS" if success else "FAILED"
        self.log_action(
            action_type=f"SERVICE_RESTART.{service_name}",
            status=status,
            details=details,
            message=message
        )
    
    def log_system_healing(self, action_type, success, message, details=None):
        """Enregistre spécifiquement une action de réparation système"""
        status = "SUCCESS" if success else "FAILED"
        self.log_action(
            action_type=f"SYSTEM_HEALING.{action_type}",
            status=status,
            details=details,
            message=message
        )