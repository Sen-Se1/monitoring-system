# Rapport de Projet - Système de Surveillance et d'Auto-Réparation

## 📋 Table des Matières
- [Introduction](#introduction)
- [Architecture du Système](#architecture-du-système)
- [Fonctionnalités](#fonctionnalités)
- [Installation et Configuration](#installation-et-configuration)
- [Utilisation](#utilisation)
- [Structure du Projet](#structure-du-projet)
- [Détails Techniques](#détails-techniques)
- [Dépannage](#dépannage)
- [Améliorations Futures](#améliorations-futures)

## 🚀 Introduction

Ce projet est un **système de surveillance complet** développé en Python qui permet de monitorer en temps réel les ressources système et les services, avec des capacités d'auto-réparation et un tableau de bord interactif.

### Objectifs
- Surveillance continue des métriques système (CPU, mémoire, disque, réseau)
- Monitoring de l'état des services critiques
- Système d'alertes intelligent avec notifications email
- Capacités d'auto-réparation automatique
- Tableau de bord visuel en temps réel
- Logging structuré en format JSON

## 🏗 Architecture du Système

### Composants Principaux

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Monitoring    │───▶│  Gestionnaire    │───▶│  Auto-Réparation │
│    (Système)    │    │    d'Alertes     │    │   (Healing)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Monitoring    │    │     Logger       │    │ Tableau de Bord │
│   (Services)    │    │     JSON         │    │   Dashboard     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Flux de Données
1. **Collecte** → Métriques système et état des services
2. **Analyse** → Comparaison avec les seuils configurés
3. **Alerte** → Notification en cas de dépassement
4. **Action** → Auto-réparation si activée
5. **Visualisation** → Affichage dans le tableau de bord

## ⚙️ Fonctionnalités

### 🔍 Surveillance
- **Métriques Système** :
  - Utilisation CPU (%)
  - Utilisation mémoire (%)
  - Espace disque disponible (%)
  - Trafic réseau (upload/download)
- **Services** : État des services systemd configurés
- **Intervale Configurable** : De 10 secondes à plusieurs minutes

### 🚨 Système d'Alerte
- **Seuils Personnalisables** : CPU, mémoire, disque, réseau
- **Niveaux de Sévérité** : Avertissement et Critique
- **Notifications Email** : Avec système anti-spam intégré
- **Alertes Contextuelles** : Messages détaillés avec timestamps

### 🔧 Auto-Réparation
- **Redémarrage Automatique** des services arrêtés
- **Nettoyage Intelligent** des fichiers temporaires
- **Gestion de la Mémoire** : Terminaison des processus gourmands
- **Vidage des Caches** système

### 📊 Tableau de Bord
- **Métriques Temps Réel** : Graphiques interactifs
- **Historique** : Évolution des performances
- **Statut des Services** : Vue d'ensemble colorée
- **Alertes Actives** : Liste des incidents en cours
- **Actions Récentes** : Journal des réparations

## 🛠 Installation et Configuration

### Prérequis
- Python 3.8 ou supérieur
- Système d'exploitation : Linux (recommandé) ou Windows
- Accès administrateur pour la surveillance des services

### Installation Automatisée

#### 🪟 Windows
```powershell
.\start.ps1
```

#### 🐧 Linux
```bash
chmod +x start.sh
./start.sh
```

### Installation Manuelle
```bash
# Création de l'environnement virtuel
python -m venv venv

# Activation
# Windows
venv\Scripts\activate
# Linux
source venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt

# Création des dossiers
mkdir -p logs
```

### Configuration

Modifier le fichier `.env` :

```ini
# Intervalle de surveillance (secondes)
MONITORING_INTERVAL=10

# Seuils d'alerte
CPU_THRESHOLD=80.0
MEMORY_THRESHOLD=85.0
DISK_THRESHOLD=90.0
NETWORK_THRESHOLD=100.0

# Services à surveiller
MONITORED_SERVICES=cron,dbus,apache2,nginx

# Auto-réparation
AUTO_HEALING_ENABLED=True

# Configuration Email
EMAIL_ALERTS_ENABLED=True
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SENDER=votre@email.com
EMAIL_SENDER_PASSWORD=votre_mot_de_passe_app
EMAIL_RECIPIENTS=destinataire@email.com
```

## 🎯 Utilisation

### Lancement Complet
```bash
python main.py
```

### Composants Individuels

#### Surveillance Seule
```bash
python monitoring/monitor.py
```

#### Tableau de Bord Seul
```bash
python visualization/dashboard.py
```

### Accès au Tableau de Bord
- **URL** : http://localhost:8050
- **Port Configurable** : Modifiable dans `main.py`
- **Rafraîchissement Automatique** : Toutes les 5 secondes

## 📁 Structure du Projet (Corrigée)

```
monitoring-system/
├── 📊 main.py                    # Point d'entrée principal
├── 📋 requirements.txt          # Dépendances Python
├── 🔐 .env                      # Variables d'environnement
├── 📄 README.md                 # Documentation
├── 🚀 start.ps1                 # Script d'installation Windows
├── 🐧 start.sh                  # Script d'installation Linux
├── 📁 monitoring/               # Modules de surveillance
│   ├── 🖥️ system_monitor.py    # Métriques système
│   ├── 🔌 service_monitor.py   # Surveillance services
│   ├── 🚨 alert_manager.py     # Gestionnaire d'alertes
│   └── 🔧 monitor.py           # Système de surveillance principal
├── 📁 visualization/            # Interface utilisateur
│   └── 📈 dashboard.py         # Tableau de bord interactif
├── 📁 config/                   # Configuration
│   └── ⚙️ settings.py          # Paramètres de configuration
├── 📁 autohealing/             # Modules d'auto-réparation
│   ├── 🔧 service_healer.py    # Réparation services
│   ├── 🛠️ system_healer.py    # Réparation système
│   ├── 📝 action_logger.py    # Journal des actions
│   └── ⚡ triggers.py          # Déclencheurs
├── 📁 utils/                   # Utilitaires
│   ├── 📝 json_array_logger.py # Logger JSON
│   └── 📧 email_sender.py     # Envoi d'emails
└── 📁 logs/                    # Fichiers de log
    └ 📄 monitoring.json       # Logs structurés JSON
```

## 🔧 Détails Techniques

### Technologies Utilisées

# **Langage et Environnement**
- **Python 3.8+** : Langage de programmation principal pour le développement du système
- **Virtual Environment** : Isolation des dépendances et gestion des packages

# **Surveillance et Métriques Système**
- **psutil** : Collecte des métriques système (CPU, mémoire, disque, réseau, processus)
- **subprocess** : Exécution de commandes système et gestion des services
- **platform** : Détection du système d'exploitation et informations hardware

# **Tableau de Bord et Visualisation**
- **Dash** : Framework web pour créer des applications analytiques interactives
- **Plotly** : Bibliothèque de visualisation pour graphiques interactifs et temps réel
- **Pandas** : Manipulation et analyse des données pour le traitement des métriques
- **Dash Bootstrap Components** : Composants UI responsives pour l'interface

# **Gestion des Données et Logging**
- **JSON** : Format de logging structuré pour le stockage des événements
- **datetime** : Gestion des horodatages et calculs temporels
- **threading** : Exécution parallèle pour la surveillance et le dashboard

# **Notification et Communication**
- **smtplib** : Envoi de notifications email via protocole SMTP/TLS
- **email.mime** : Formatage des messages email avec support HTML

# **Configuration et Gestion**
- **python-dotenv** : Chargement des variables d'environnement depuis le fichier .env
- **os** : Interactions avec le système de fichiers et variables d'environnement

# **Utilitaires et Sécurité**
- **re** : Expressions régulières pour le nettoyage des données
- **glob** : Recherche de fichiers avec patterns pour le nettoyage automatique
- **time** : Gestion des intervalles et pauses dans la surveillance

### Modules Clés

#### 📊 monitoring/monitor.py
**Fonctionnalités principales :**
- Orchestration de la surveillance complète
- Coordination entre les différents modules
- Gestion du cycle de surveillance
- Affichage unifié des résultats

**Points forts :**
- Gestion centralisée des logs JSON
- Intégration transparente avec l'auto-réparation
- Affichage cohérent dans la console

#### 📈 visualization/dashboard.py
**Fonctionnalités principales :**
- Interface web interactive avec Dash
- Graphiques temps réel avec Plotly
- Mise à jour automatique toutes les 5 secondes
- Visualisation des métriques historiques

**Composants :**
- Métriques système en temps réel
- État des services
- Historique des alertes
- Journal des actions d'auto-réparation

#### ⚙️ config/settings.py
**Configuration centralisée :**
- Chargement des variables d'environnement
- Définition des seuils de surveillance
- Configuration des services monitorés
- Paramètres d'auto-réparation et d'email

### Format des Logs JSON
```json
{
  "timestamp": "2024-01-15T10:30:00.000000",
  "event_type": "alert",
  "alert_type": "high_cpu",
  "severity": "CRITIQUE",
  "message": "CPU élevé: 95.2%",
  "details": {
    "value": 95.2,
    "threshold": 80.0
  }
}
```

### Sécurité
- **Connexions SMTP sécurisées** (TLS)
- **Mots de passe dans .env** (non commités)
- **Validation des entrées** dans les modules
- **Gestion des erreurs** robuste

## 🐛 Dépannage

### Problèmes Courants

#### ❌ Services Non Détectés (Windows)
**Symptôme** : Erreurs "systemctl not found"
**Solution** : Adapter `service_monitor.py` pour utiliser PowerShell

#### 📧 Emails Non Reçus
**Vérifier** :
- Paramètres SMTP dans `.env`
- Mot de passe d'application Gmail
- Pare-feu/antivirus

#### 📊 Tableau de Bord Inaccessible
**Vérifier** :
- Port 8050 disponible
- Logs dans `logs/monitoring.json`

### Commandes de Diagnostic
```bash
# Vérifier les logs
tail -f logs/monitoring.log

# Tester les métriques
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%')"

# Vérifier les services
systemctl status apache2
```

## 🚀 Améliorations Futures

### 🔮 Fonctionnalités Planifiées

#### Surveillance Avancée
- [ ] Surveillance des conteneurs Docker
- [ ] Métriques base de données
- [ ] Surveillance des applications web
- [ ] Métriques réseau avancées (latence, paquets perdus)

#### Alertes et Notifications
- [ ] Notifications Slack/Teams
- [ ] SMS via API
- [ ] Escalade d'alertes
- [ ] Alertes intelligentes (machine learning)

#### Auto-Réparation
- [ ] Scripts de réparation personnalisables
- [ ] Rollback automatique
- [ ] Diagnostic automatique des pannes
- [ ] Orchestration de redémarrage

#### Interface Utilisateur
- [ ] Application mobile
- [ ] API REST complète
- [ ] Rapports PDF automatiques
- [ ] Tableaux de bord personnalisables

#### Sécurité et Performance
- [ ] Authentification utilisateur
- [ ] Chiffrement des données sensibles
- [ ] Cluster pour haute disponibilité
- [ ] Base de données temps-réel

### 📈 Métriques d'Évolution
- **Couverture** : Passer de 4 à 15+ métriques surveillées
- **Performance** : Réduction du temps de réponse à < 1s
- **Disponibilité** : Objectif 99.9% uptime
- **Automatisation** : 95% des incidents résolus automatiquement

## 📞 Support et Contribution

### Documentation
- 📚 Documentation complète dans `README.md`
- 🔗 Wiki du projet (à créer)
- 💡 Exemples de configuration

### Communauté
- 🐛 Signaler des bugs via GitHub Issues
- 💡 Proposer des fonctionnalités
- 🔧 Contributions bienvenues

### Maintenance
- 🔄 Mises à jour de sécurité mensuelles
- 📦 Releases trimestrielles
- 🛠 Support technique actif

---

## 📄 Licence

Ce projet est distribué sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Auteurs

**Équipe de Développement**  
- Développement principal et architecture  
- Modules de surveillance et d'auto-réparation  
- Interface utilisateur et tableau de bord  