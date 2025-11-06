import psutil
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.last_network_io = psutil.net_io_counters()
        self.last_check = datetime.now()
    
    def check_cpu(self):
        """Vérifie l'utilisation du CPU"""
        return psutil.cpu_percent(interval=1)
    
    def check_memory(self):
        """Vérifie l'utilisation de la mémoire"""
        return psutil.virtual_memory().percent
    
    def check_disk(self):
        """Vérifie l'utilisation du disque"""
        return psutil.disk_usage('/').percent
    
    def check_network(self):
        """Vérifie l'utilisation du réseau"""
        current_io = psutil.net_io_counters()
        
        # Calcul de l'utilisation depuis le dernier check
        time_diff = (datetime.now() - self.last_check).total_seconds()
        
        sent_mb = (current_io.bytes_sent - self.last_network_io.bytes_sent) / (1024 * 1024)
        recv_mb = (current_io.bytes_recv - self.last_network_io.bytes_recv) / (1024 * 1024)
        
        # Mise à jour pour le prochain check
        self.last_network_io = current_io
        self.last_check = datetime.now()
        
        return {
            'sent_mb': round(sent_mb, 2),
            'recv_mb': round(recv_mb, 2),
            'bytes_sent': current_io.bytes_sent,
            'bytes_recv': current_io.bytes_recv
        }
    
    def check_all_metrics(self):
        """Vérifie toutes les métriques système"""
        return {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'cpu': self.check_cpu(),
            'memory': self.check_memory(),
            'disk': self.check_disk(),
            'network': self.check_network()
        }
    
    def get_detailed_metrics(self):
        """Retourne des métriques détaillées"""
        return {
            'cpu_cores': psutil.cpu_count(),
            'cpu_freq': psutil.cpu_freq().current if psutil.cpu_freq() else None,
            'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'disk_total_gb': round(psutil.disk_usage('/').total / (1024**3), 2),
            'process_count': len(psutil.pids())
        }