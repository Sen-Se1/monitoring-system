import os
from dotenv import load_dotenv

load_dotenv()

MONITORING_INTERVAL = int(os.getenv('MONITORING_INTERVAL', 10))
CPU_THRESHOLD = float(os.getenv('CPU_THRESHOLD', 80.0))
MEMORY_THRESHOLD = float(os.getenv('MEMORY_THRESHOLD', 85.0))
DISK_THRESHOLD = float(os.getenv('DISK_THRESHOLD', 90.0))
NETWORK_THRESHOLD = float(os.getenv('NETWORK_THRESHOLD', 100.0))

MONITORED_SERVICES = [s.strip() for s in os.getenv('MONITORED_SERVICES', 'cron,dbus,apache2').split(',')]

LOG_FILE = os.getenv('LOG_FILE', 'logs/monitoring.json')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

AUTO_HEALING_ENABLED = os.getenv('AUTO_HEALING_ENABLED', 'True').lower() == 'true'
CLEANUP_PATHS = [p.strip() for p in os.getenv('CLEANUP_PATHS', '/tmp,/var/tmp,/home/*/tmp').split(',')]

AUTO_HEAL_CPU_THRESHOLD = float(os.getenv('AUTO_HEAL_CPU_THRESHOLD', 90.0))
AUTO_HEAL_MEMORY_THRESHOLD = float(os.getenv('AUTO_HEAL_MEMORY_THRESHOLD', 95.0))
AUTO_HEAL_DISK_THRESHOLD = float(os.getenv('AUTO_HEAL_DISK_THRESHOLD', 95.0))