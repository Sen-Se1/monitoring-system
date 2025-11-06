# Configuration de surveillance
MONITORING_INTERVAL = 60  # secondes
CPU_THRESHOLD = 80.0
MEMORY_THRESHOLD = 85.0
DISK_THRESHOLD = 90.0

# Services à surveiller
MONITORED_SERVICES = ["ssh", "cron", "dbus", "network-manager"]

# Configuration des logs
LOG_FILE = "logs/monitoring.log"
LOG_LEVEL = "INFO"