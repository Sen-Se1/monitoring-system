# Configuration de surveillance
MONITORING_INTERVAL = 60  # secondes
CPU_THRESHOLD = 80.0
MEMORY_THRESHOLD = 85.0
DISK_THRESHOLD = 90.0
NETWORK_THRESHOLD = 100.0  # MB par intervalle

# Services à surveiller
MONITORED_SERVICES = ["ssh", "cron", "dbus", "network-manager"]

# Configuration des logs
LOG_FILE = "logs/monitoring.log"
LOG_LEVEL = "INFO"

# Configuration de l'auto-réparation
AUTO_HEALING_ENABLED = True
MAX_RESTART_ATTEMPTS = 3
CLEANUP_PATHS = ["/tmp", "/var/tmp", "/home/*/tmp"]
LOG_ACTIONS_ENABLED = True
ACTION_LOG_FILE = "logs/actions.log"

# Seuils pour l'auto-réparation
AUTO_HEAL_CPU_THRESHOLD = 90.0      # CPU > 90% déclenche le nettoyage cache
AUTO_HEAL_MEMORY_THRESHOLD = 95.0   # Mémoire > 95% déclenche kill process
AUTO_HEAL_DISK_THRESHOLD = 95.0     # Disque > 95% déclenche nettoyage fichiers