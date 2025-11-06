import subprocess
import logging
import shutil
import os
import glob
from datetime import datetime

logger = logging.getLogger(__name__)

class SystemHealer:
    def __init__(self, cleanup_paths=None):
        self.cleanup_paths = cleanup_paths or ["/tmp", "/var/tmp"]
        self.cleanup_actions = 0
        self.cache_clears = 0
        self.process_kills = 0
    
    def cleanup_temp_files(self):
        """Nettoie les fichiers temporaires pour libérer de l'espace disque"""
        try:
            total_freed = 0
            cleaned_paths = []
            
            logger.info("🧹 Nettoyage des fichiers temporaires...")
            
            for path_pattern in self.cleanup_paths:
                try:
                    # Expansion des patterns glob
                    paths = glob.glob(path_pattern)
                    
                    for path in paths:
                        if os.path.exists(path):
                            # Calcul de la taille avant nettoyage
                            before_size = self._get_directory_size(path)
                            
                            # Nettoyage sécurisé - seulement les fichiers de plus de 1 jour
                            files_removed = 0
                            for root, dirs, files in os.walk(path):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    try:
                                        if os.path.isfile(file_path):
                                            file_age = datetime.now().timestamp() - os.path.getmtime(file_path)
                                            if file_age > 86400:  # 1 jour en secondes
                                                os.remove(file_path)
                                                files_removed += 1
                                    except (OSError, PermissionError):
                                        pass
                            
                            # Calcul de la taille après nettoyage
                            after_size = self._get_directory_size(path)
                            freed = before_size - after_size
                            total_freed += freed
                            
                            if freed > 0:
                                cleaned_paths.append({
                                    'path': path,
                                    'freed_bytes': freed,
                                    'freed_mb': round(freed / (1024 * 1024), 2),
                                    'files_removed': files_removed
                                })
                                
                except Exception as e:
                    logger.warning(f"Impossible de nettoyer {path_pattern}: {e}")
            
            self.cleanup_actions += 1
            
            if total_freed > 0:
                freed_mb = round(total_freed / (1024 * 1024), 2)
                logger.info(f"✅ Nettoyage terminé: {freed_mb} MB libérés")
                
                action_details = {
                    'action': 'cleanup_temp_files',
                    'status': 'success',
                    'freed_mb': freed_mb,
                    'cleaned_paths': cleaned_paths,
                    'timestamp': datetime.now().isoformat()
                }
                return True, f"{freed_mb} MB libérés", action_details
            else:
                logger.info("ℹ️ Aucun fichier à nettoyer")
                
                action_details = {
                    'action': 'cleanup_temp_files',
                    'status': 'no_action',
                    'message': 'Aucun fichier à nettoyer',
                    'timestamp': datetime.now().isoformat()
                }
                return True, "Aucun fichier à nettoyer", action_details
                
        except Exception as e:
            error_msg = f"Erreur lors du nettoyage: {e}"
            logger.error(error_msg)
            
            action_details = {
                'action': 'cleanup_temp_files',
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False, error_msg, action_details
    
    def clear_cache(self):
        """Vide les caches système"""
        try:
            logger.info("🧠 Nettoyage des caches système...")
            
            # Synchronisation des systèmes de fichiers
            subprocess.run(['sync'], capture_output=True, timeout=10)
            
            # Libération des caches (Linux seulement)
            if os.path.exists('/proc/sys/vm/drop_caches'):
                with open('/proc/sys/vm/drop_caches', 'w') as f:
                    f.write('3')  # Nettoyer pagecache, dentries et inodes
                
                self.cache_clears += 1
                logger.info("✅ Caches système nettoyés")
                
                action_details = {
                    'action': 'clear_cache',
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                }
                return True, "Caches système nettoyés", action_details
            else:
                logger.info("ℹ️ Nettoyage des caches non supporté sur ce système")
                
                action_details = {
                    'action': 'clear_cache',
                    'status': 'not_supported',
                    'message': 'Nettoyage des caches non supporté',
                    'timestamp': datetime.now().isoformat()
                }
                return True, "Nettoyage des caches non supporté", action_details
                
        except Exception as e:
            error_msg = f"Erreur lors du nettoyage des caches: {e}"
            logger.error(error_msg)
            
            action_details = {
                'action': 'clear_cache',
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False, error_msg, action_details
    
    def kill_process_by_memory(self, threshold_percent=10.0):
        """Tue les processus utilisant trop de mémoire"""
        try:
            import psutil
            
            logger.info(f"🔪 Recherche de processus utilisant plus de {threshold_percent}% de mémoire...")
            
            processes_to_kill = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'username']):
                try:
                    if proc.info['memory_percent'] > threshold_percent:
                        # Éviter de tuer les processus système importants
                        if proc.info['username'] not in ['root', 'system'] and \
                           proc.info['name'] not in ['systemd', 'kernel']:
                            processes_to_kill.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            if processes_to_kill:
                # Trier par utilisation mémoire (descendant)
                processes_to_kill.sort(key=lambda x: x['memory_percent'], reverse=True)
                
                # Ne tuer que le processus le plus gourmand
                target_process = processes_to_kill[0]
                logger.warning(f"🚨 Processus gourmand détecté: {target_process['name']} (PID: {target_process['pid']}) - {target_process['memory_percent']:.1f}% mémoire")
                
                try:
                    os.kill(target_process['pid'], 9)
                    self.process_kills += 1
                    logger.info(f"✅ Processus {target_process['name']} (PID: {target_process['pid']}) terminé")
                    
                    action_details = {
                        'action': 'kill_process',
                        'status': 'success',
                        'process_name': target_process['name'],
                        'process_pid': target_process['pid'],
                        'memory_usage': target_process['memory_percent'],
                        'timestamp': datetime.now().isoformat()
                    }
                    return True, f"Processus {target_process['name']} terminé", action_details
                except Exception as e:
                    error_msg = f"Impossible de tuer le processus {target_process['name']}: {e}"
                    logger.error(error_msg)
                    
                    action_details = {
                        'action': 'kill_process',
                        'status': 'failed',
                        'process_name': target_process['name'],
                        'process_pid': target_process['pid'],
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                    return False, error_msg, action_details
            else:
                logger.info("ℹ️ Aucun processus gourmand détecté")
                
                action_details = {
                    'action': 'kill_process',
                    'status': 'no_action',
                    'message': 'Aucun processus gourmand détecté',
                    'timestamp': datetime.now().isoformat()
                }
                return True, "Aucun processus gourmand détecté", action_details
                
        except Exception as e:
            error_msg = f"Erreur lors de la gestion des processus: {e}"
            logger.error(error_msg)
            
            action_details = {
                'action': 'kill_process',
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return False, error_msg, action_details
    
    def _get_directory_size(self, path):
        """Calcule la taille d'un répertoire"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except OSError:
                    pass
        return total_size
    
    def get_healing_stats(self):
        """Retourne les statistiques de réparation système"""
        return {
            'cleanup_actions': self.cleanup_actions,
            'cache_clears': self.cache_clears,
            'process_kills': self.process_kills
        }