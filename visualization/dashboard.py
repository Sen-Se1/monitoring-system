import json
import os
import time
import threading
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

class MonitoringDashboard:
    def __init__(self, log_file="logs/monitoring.json", port=8050):
        self.log_file = log_file
        self.port = port
        self.last_modified = 0
        self.data = []
        
    def load_data(self):
        """Charge les données depuis le fichier JSON"""
        try:
            if os.path.exists(self.log_file) and os.path.getsize(self.log_file) > 0:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Erreur lecture données: {e}")
            self.data = []
    
    def get_system_metrics(self):
        """Extrait les métriques système"""
        system_data = []
        for entry in self.data:
            if entry.get('event_type') == 'metric' and entry.get('metric_type') == 'system':
                system_data.append({
                    'timestamp': entry['timestamp'],
                    'cpu': entry['values']['cpu_percent'],
                    'memory': entry['values']['memory_percent'],
                    'disk': entry['values']['disk_percent'],
                    'network': entry['values']['total_network_mb']
                })
        return pd.DataFrame(system_data)
    
    def get_alerts(self):
        """Extrait les alertes"""
        alerts = []
        for entry in self.data:
            if entry.get('event_type') == 'alert':
                alerts.append({
                    'timestamp': entry['timestamp'],
                    'type': entry['alert_type'],
                    'severity': entry['severity'],
                    'message': entry['message'],
                    'service': entry['details'].get('service', 'N/A')
                })
        return pd.DataFrame(alerts)
    
    def get_actions(self):
        """Extrait les actions"""
        actions = []
        for entry in self.data:
            if entry.get('event_type') == 'action':
                actions.append({
                    'timestamp': entry['timestamp'],
                    'type': entry['action_type'],
                    'status': entry['status'],
                    'message': entry['message'],
                    'service': entry.get('service', 'N/A')
                })
        return pd.DataFrame(actions)
    
    def get_service_status(self):
        """Extrait le statut des services"""
        service_data = []
        for entry in self.data:
            if entry.get('event_type') == 'metric' and entry.get('metric_type') == 'service_status':
                service_data.append({
                    'timestamp': entry['timestamp'],
                    'service': entry['values']['service'],
                    'status': entry['values']['status']
                })
        return pd.DataFrame(service_data)
    
    def create_system_metrics_chart(self):
        """Crée le graphique des métriques système"""
        df = self.get_system_metrics()
        if df.empty:
            return go.Figure().add_annotation(text="Aucune donnée disponible", showarrow=False)
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Utilisation CPU (%)', 'Utilisation Mémoire (%)', 
                          'Utilisation Disque (%)', 'Trafic Réseau (MB)'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # CPU
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['cpu'], name='CPU', line=dict(color='red')),
            row=1, col=1
        )
        
        # Mémoire
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['memory'], name='Mémoire', line=dict(color='blue')),
            row=1, col=2
        )
        
        # Disque
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['disk'], name='Disque', line=dict(color='green')),
            row=2, col=1
        )
        
        # Réseau
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['network'], name='Réseau', line=dict(color='purple')),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=False, title_text="Évolution des Métriques Système")
        return fig
    
    def create_alerts_chart(self):
        """Crée le graphique des alertes"""
        df = self.get_alerts()
        if df.empty:
            return go.Figure().add_annotation(text="Aucune alerte enregistrée", showarrow=False)
        
        # Alertes par type
        alert_counts = df['type'].value_counts()
        fig1 = px.pie(values=alert_counts.values, names=alert_counts.index, 
                     title="Répartition des Alertes par Type")
        
        # Alertes par sévérité
        severity_counts = df['severity'].value_counts()
        fig2 = px.bar(x=severity_counts.index, y=severity_counts.values,
                     title="Alertes par Sévérité", color=severity_counts.index,
                     color_discrete_map={'CRITIQUE': 'red', 'AVERTISSEMENT': 'orange'})
        
        return fig1, fig2
    
    def create_actions_chart(self):
        """Crée le graphique des actions"""
        df = self.get_actions()
        if df.empty:
            return go.Figure().add_annotation(text="Aucune action enregistrée", showarrow=False)
        
        # Actions par type et statut
        action_status = df.groupby(['type', 'status']).size().reset_index(name='count')
        fig = px.bar(action_status, x='type', y='count', color='status',
                    title="Actions par Type et Statut",
                    color_discrete_map={'SUCCESS': 'green', 'FAILED': 'red'})
        
        return fig
    
    def create_service_status_chart(self):
        """Crée le graphique du statut des services"""
        df = self.get_service_status()
        if df.empty:
            return go.Figure().add_annotation(text="Aucun statut de service enregistré", showarrow=False)
        
        # Dernier statut de chaque service
        latest_status = df.sort_values('timestamp').groupby('service').last().reset_index()
        
        fig = px.bar(latest_status, x='service', y=[1]*len(latest_status), color='status',
                    title="Statut Actuel des Services",
                    color_discrete_map={'active': 'green', 'inactive': 'red'},
                    labels={'y': ''})
        
        fig.update_layout(showlegend=True)
        return fig
    
    def create_dashboard(self):
        """Crée le tableau de bord Dash"""
        app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
        
        app.layout = dbc.Container([
            dbc.Row([
                dbc.Col(html.H1("📊 Tableau de Bord - Surveillance Système", 
                               className="text-center mb-4"), width=12)
            ]),
            
            # Métriques en temps réel
            dbc.Row([
                dbc.Col(html.Div(id="live-metrics"), width=12)
            ], className="mb-4"),
            
            # Graphiques principaux
            dbc.Row([
                dbc.Col(dcc.Graph(id="system-metrics-chart"), width=12, className="mb-4"),
            ]),
            
            dbc.Row([
                dbc.Col(dcc.Graph(id="alerts-pie-chart"), width=6),
                dbc.Col(dcc.Graph(id="alerts-bar-chart"), width=6),
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col(dcc.Graph(id="actions-chart"), width=6),
                dbc.Col(dcc.Graph(id="service-status-chart"), width=6),
            ]),
            
            # Intervalle de mise à jour
            dcc.Interval(
                id='interval-component',
                interval=5*1000,  # 5 secondes
                n_intervals=0
            )
        ], fluid=True)
        
        @app.callback(
            [Output('system-metrics-chart', 'figure'),
             Output('alerts-pie-chart', 'figure'),
             Output('alerts-bar-chart', 'figure'),
             Output('actions-chart', 'figure'),
             Output('service-status-chart', 'figure'),
             Output('live-metrics', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_dashboard(n):
            # Recharger les données si le fichier a été modifié
            current_modified = os.path.getmtime(self.log_file) if os.path.exists(self.log_file) else 0
            if current_modified > self.last_modified:
                self.load_data()
                self.last_modified = current_modified
            
            # Créer les graphiques
            system_fig = self.create_system_metrics_chart()
            alerts_fig1, alerts_fig2 = self.create_alerts_chart()
            actions_fig = self.create_actions_chart()
            service_fig = self.create_service_status_chart()
            
            # Métriques en temps réel
            df_system = self.get_system_metrics()
            df_alerts = self.get_alerts()
            df_actions = self.get_actions()
            
            if not df_system.empty:
                latest_metrics = df_system.iloc[-1]
                live_metrics = dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col(html.H4(f"CPU: {latest_metrics['cpu']:.1f}%", 
                                          style={'color': 'red' if latest_metrics['cpu'] > 80 else 'green'}), width=3),
                            dbc.Col(html.H4(f"Mémoire: {latest_metrics['memory']:.1f}%", 
                                          style={'color': 'red' if latest_metrics['memory'] > 85 else 'green'}), width=3),
                            dbc.Col(html.H4(f"Disque: {latest_metrics['disk']:.1f}%", 
                                          style={'color': 'red' if latest_metrics['disk'] > 90 else 'green'}), width=3),
                            dbc.Col(html.H4(f"Réseau: {latest_metrics['network']:.1f}MB", 
                                          style={'color': 'orange'}), width=3),
                        ]),
                        dbc.Row([
                            dbc.Col(html.H5(f"Alertes: {len(df_alerts)}"), width=3),
                            dbc.Col(html.H5(f"Actions: {len(df_actions)}"), width=3),
                            dbc.Col(html.H5(f"Services: {len(self.get_service_status()['service'].unique())}"), width=3),
                            dbc.Col(html.H5(f"Dernière MAJ: {datetime.now().strftime('%H:%M:%S')}"), width=3),
                        ])
                    ])
                ], color="light")
            else:
                live_metrics = dbc.Alert("En attente de données...", color="warning")
            
            return system_fig, alerts_fig1, alerts_fig2, actions_fig, service_fig, live_metrics
        
        return app
    
    def run_dashboard(self):
        """Lance le tableau de bord"""
        print(f"🚀 Démarrage du tableau de bord sur http://localhost:{self.port}")
        app = self.create_dashboard()
        app.run_server(debug=False, host='0.0.0.0', port=self.port)