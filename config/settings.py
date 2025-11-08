import os
from dotenv import load_dotenv

load_dotenv()

# Configuration de surveillance
MONITORING_INTERVAL = int(os.getenv('MONITORING_INTERVAL', 10))
CPU_THRESHOLD = float(os.getenv('CPU_THRESHOLD', 80.0))
MEMORY_THRESHOLD = float(os.getenv('MEMORY_THRESHOLD', 85.0))
DISK_THRESHOLD = float(os.getenv('DISK_THRESHOLD', 90.0))
NETWORK_THRESHOLD = float(os.getenv('NETWORK_THRESHOLD', 100.0))

# Services à surveiller
MONITORED_SERVICES = [s.strip() for s in os.getenv('MONITORED_SERVICES', 'cron,dbus,apache2').split(',')]

# Configuration des logs - FORMAT JSON ARRAY MAINTENANT
LOG_FILE = os.getenv('LOG_FILE', 'logs/monitoring.json')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Configuration de l'auto-réparation
AUTO_HEALING_ENABLED = os.getenv('AUTO_HEALING_ENABLED', 'True').lower() == 'true'
CLEANUP_PATHS = [p.strip() for p in os.getenv('CLEANUP_PATHS', '/tmp,/var/tmp,/home/*/tmp').split(',')]

# Seuils pour l'auto-réparation
AUTO_HEAL_CPU_THRESHOLD = float(os.getenv('AUTO_HEAL_CPU_THRESHOLD', 90.0))
AUTO_HEAL_MEMORY_THRESHOLD = float(os.getenv('AUTO_HEAL_MEMORY_THRESHOLD', 95.0))
AUTO_HEAL_DISK_THRESHOLD = float(os.getenv('AUTO_HEAL_DISK_THRESHOLD', 95.0))

# Configuration Email
EMAIL_ALERTS_ENABLED = os.getenv('EMAIL_ALERTS_ENABLED', 'False').lower() == 'true'
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', 587))
EMAIL_SENDER = os.getenv('EMAIL_SENDER', '')
EMAIL_SENDER_PASSWORD = os.getenv('EMAIL_SENDER_PASSWORD', '')
EMAIL_RECIPIENTS = [email.strip() for email in os.getenv('EMAIL_RECIPIENTS', '').split(',') if email.strip()]
EMAIL_ALERT_INTERVAL = int(os.getenv('EMAIL_ALERT_INTERVAL', 300))