class ActionLogger:
    def __init__(self, enabled=True, json_logger=None):
        self.enabled = enabled
        self.json_logger = json_logger
    
    def log_action(self, action_type, status, details=None, message=""):
        """Enregistre une action d'auto-réparation via le logger JSON (sans console)"""
        if not self.enabled or not self.json_logger:
            return
        
        self.json_logger.log_action(
            action_type=action_type,
            status=status,
            message=message,
            details=details
        )
        # REMOVED: No console output here - let monitor.py handle display
    
    def log_service_restart(self, service_name, success, message, details=None):
        """Enregistre spécifiquement un redémarrage de service (sans console)"""
        status = "SUCCESS" if success else "FAILED"
        self.log_action(
            action_type=f"service_restart",
            status=status,
            details=details,
            message=message
        )
    
    def log_system_healing(self, action_type, success, message, details=None):
        """Enregistre spécifiquement une action de réparation système (sans console)"""
        status = "SUCCESS" if success else "FAILED"
        self.log_action(
            action_type=action_type,
            status=status,
            details=details,
            message=message
        )