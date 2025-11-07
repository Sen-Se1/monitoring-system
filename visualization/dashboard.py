import json
import os
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
                    'service': entry['details'].get('service', 'Système')
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
                    'service': entry.get('service', 'Système')
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
    
    def get_latest_service_status(self):
        """Récupère le dernier statut de chaque service"""
        df = self.get_service_status()
        if df.empty:
            return []
        
        # Obtenir le dernier statut pour chaque service
        latest_status = df.sort_values('timestamp').groupby('service').last().reset_index()
        return latest_status.to_dict('records')
    
    def get_recent_alerts(self, limit=10):
        """Récupère les alertes récentes"""
        df = self.get_alerts()
        if df.empty:
            return []
        
        return df.sort_values('timestamp', ascending=False).head(limit).to_dict('records')
    
    def get_recent_actions(self, limit=10):
        """Récupère les actions récentes"""
        df = self.get_actions()
        if df.empty:
            return []
        
        return df.sort_values('timestamp', ascending=False).head(limit).to_dict('records')
    
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
        
        fig.update_layout(height=400, showlegend=False, title_text="Évolution des Métriques Système")
        return fig
    
    def create_alerts_by_service_chart(self):
        """Crée le graphique des alertes par service"""
        df = self.get_alerts()
        if df.empty:
            return go.Figure().add_annotation(text="Aucune alerte enregistrée", showarrow=False)
        
        # Alertes par service
        service_counts = df['service'].value_counts()
        fig = px.bar(x=service_counts.index, y=service_counts.values,
                     title="Nombre d'Incidents par Service",
                     labels={'x': 'Service', 'y': "Nombre d'Alertes"},
                     color=service_counts.values,
                     color_continuous_scale='reds')
        fig.update_layout(showlegend=False, height=300)
        return fig
    
    def create_actions_chart(self):
        """Crée le graphique des actions"""
        df = self.get_actions()
        if df.empty:
            return go.Figure().add_annotation(text="Aucune action enregistrée", showarrow=False)
        
        # Actions par type et statut
        action_status = df.groupby(['type', 'status']).size().reset_index(name='count')
        fig = px.bar(action_status, x='type', y='count', color='status',
                    title="Actions par Type et Statut",
                    labels={'type': "Type d'Action", 'count': 'Nombre'},
                    color_discrete_map={'SUCCESS': 'green', 'FAILED': 'red'})
        fig.update_layout(height=300)
        return fig
    
    def create_service_status_table(self):
        """Crée un tableau HTML pour l'état des services"""
        services = self.get_latest_service_status()
        
        if not services:
            return html.Div("Aucun service surveillé", className="text-muted")
        
        rows = []
        for service in services:
            status_icon = "🟢" if service['status'] == 'active' else "🔴"
            status_text = "Actif" if service['status'] == 'active' else "Arrêté"
            status_color = "success" if service['status'] == 'active' else "danger"
            
            row = dbc.ListGroupItem([
                html.Div([
                    html.Span(status_icon, style={'fontSize': '20px', 'marginRight': '10px'}),
                    html.Strong(service['service']),
                    html.Span(status_text, className=f"badge bg-{status_color} ms-2")
                ], className="d-flex justify-content-between align-items-center")
            ])
            rows.append(row)
        
        return dbc.ListGroup(rows, flush=True)
    
    def create_alerts_table(self):
        """Crée un tableau HTML pour les alertes"""
        alerts = self.get_recent_alerts(10)
        
        if not alerts:
            return html.Div([
                html.Div("✅ Aucune alerte active", className="text-success text-center p-3")
            ], style={'border': '1px solid #28a745', 'borderRadius': '5px'})
        
        rows = []
        for alert in alerts:
            severity_icon = "🔴" if alert['severity'] == 'CRITIQUE' else "🟡"
            severity_color = "danger" if alert['severity'] == 'CRITIQUE' else "warning"
            
            row = dbc.ListGroupItem([
                html.Div([
                    html.Span(severity_icon, style={'fontSize': '16px', 'marginRight': '8px'}),
                    html.Span(alert['message'], style={'flex': 1}),
                    html.Small(alert['timestamp'][11:19], className="text-muted")
                ], className="d-flex justify-content-between align-items-center")
            ], color=severity_color)
            rows.append(row)
        
        return dbc.ListGroup(rows, flush=True)
    
    def create_actions_table(self):
        """Crée un tableau HTML pour les actions d'auto-réparation"""
        actions = self.get_recent_actions(10)
        
        if not actions:
            return html.Div([
                html.Div("Aucune action récente", className="text-muted text-center p-3")
            ], style={'border': '1px solid #6c757d', 'borderRadius': '5px'})
        
        rows = []
        for action in actions:
            status_icon = "✅" if action['status'] == 'SUCCESS' else "❌"
            status_color = "success" if action['status'] == 'SUCCESS' else "danger"
            
            # Extraire le nom du service si disponible
            service_name = action.get('service', 'Système')
            if service_name and service_name != 'N/A':
                action_text = f"{service_name}: {action['message']}"
            else:
                action_text = action['message']
            
            row = dbc.ListGroupItem([
                html.Div([
                    html.Span(status_icon, style={'fontSize': '16px', 'marginRight': '8px'}),
                    html.Span(action_text, style={'flex': 1, 'fontSize': '14px'}),
                    html.Small(action['timestamp'][11:19], className="text-muted")
                ], className="d-flex justify-content-between align-items-center")
            ], color=status_color)
            rows.append(row)
        
        return dbc.ListGroup(rows, flush=True)
    
    def create_dashboard(self):
        """Crée le tableau de bord Dash"""
        app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
        
        app.layout = dbc.Container([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1("📊 Tableau de Bord - Surveillance Système", 
                           className="text-center mb-2 mt-3",
                           style={'color': '#2c3e50', 'fontWeight': 'bold'}),
                    html.Hr(style={'borderTop': '2px solid #3498db'})
                ], width=12)
            ]),
            
            # Real-time Metrics Card
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Div("⚡ MÉTRIQUES TEMPS RÉEL", 
                                            className="text-uppercase small text-muted mb-2"),
                                    html.Div(id="live-metrics-details")
                                ], width=12)
                            ])
                        ])
                    ], color="light", className="mb-4 shadow-sm")
                ], width=12)
            ]),
            
            # Main Content - Two Columns
            dbc.Row([
                # Left Column - Charts
                dbc.Col([
                    # System Metrics Chart
                    dbc.Card([
                        dbc.CardHeader("📈 Évolution des Métriques Système", 
                                      className="fw-bold bg-primary text-white"),
                        dbc.CardBody([
                            dcc.Graph(id="system-metrics-chart")
                        ])
                    ], className="mb-4 shadow-sm"),
                    
                    # Bottom Charts Row
                    dbc.Row([
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("📊 Incidents par Service", 
                                              className="fw-bold bg-warning text-dark"),
                                dbc.CardBody([
                                    dcc.Graph(id="alerts-by-service-chart")
                                ])
                            ], className="shadow-sm")
                        ], width=6),
                        dbc.Col([
                            dbc.Card([
                                dbc.CardHeader("🔧 Actions par Type", 
                                              className="fw-bold bg-info text-white"),
                                dbc.CardBody([
                                    dcc.Graph(id="actions-chart")
                                ])
                            ], className="shadow-sm")
                        ], width=6)
                    ])
                ], width=8),
                
                # Right Column - Status Panels
                dbc.Col([
                    # Service Status
                    dbc.Card([
                        dbc.CardHeader("🔧 État des Services", 
                                      className="fw-bold bg-success text-white"),
                        dbc.CardBody([
                            html.Div(id="service-status-table", 
                                    style={'maxHeight': '200px', 'overflowY': 'auto'})
                        ])
                    ], className="mb-4 shadow-sm"),
                    
                    # Recent Alerts
                    dbc.Card([
                        dbc.CardHeader("🚨 ALERTES ACTIVES", 
                                      className="fw-bold bg-danger text-white"),
                        dbc.CardBody([
                            html.Div(id="alerts-table", 
                                    style={'maxHeight': '200px', 'overflowY': 'auto'})
                        ])
                    ], className="mb-4 shadow-sm"),
                    
                    # Recent Actions
                    dbc.Card([
                        dbc.CardHeader("⚡ ACTIONS RÉCENTES", 
                                      className="fw-bold bg-secondary text-white"),
                        dbc.CardBody([
                            html.Div(id="actions-table", 
                                    style={'maxHeight': '200px', 'overflowY': 'auto'})
                        ])
                    ], className="shadow-sm")
                ], width=4)
            ]),
            
            # Footer
            dbc.Row([
                dbc.Col([
                    html.Hr(),
                    html.P("Système de Surveillance - Mise à jour automatique toutes les 5 secondes", 
                          className="text-center text-muted small mt-3")
                ], width=12)
            ]),
            
            dcc.Interval(
                id='interval-component',
                interval=5*1000,  # 5 secondes
                n_intervals=0
            )
        ], fluid=True, style={'backgroundColor': '#f8f9fa'})
        
        @app.callback(
            [Output('system-metrics-chart', 'figure'),
             Output('alerts-by-service-chart', 'figure'),
             Output('actions-chart', 'figure'),
             Output('live-metrics-details', 'children'),
             Output('service-status-table', 'children'),
             Output('alerts-table', 'children'),
             Output('actions-table', 'children')],
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
            alerts_service_fig = self.create_alerts_by_service_chart()
            actions_fig = self.create_actions_chart()
            
            # Créer les tableaux
            service_table = self.create_service_status_table()
            alerts_table = self.create_alerts_table()
            actions_table = self.create_actions_table()
            
            # Métriques en temps réel
            df_system = self.get_system_metrics()
            df_alerts = self.get_alerts()
            df_actions = self.get_actions()
            df_services = self.get_service_status()
            
            if not df_system.empty:
                latest_metrics = df_system.iloc[-1]
                
                # Create metric cards
                metrics_row = dbc.Row([
                    # CPU
                    dbc.Col([
                        html.Div([
                            html.Div("💻 CPU", className="small text-muted"),
                            html.H4(f"{latest_metrics['cpu']:.1f}%", 
                                   style={'color': 'red' if latest_metrics['cpu'] > 80 else 'green',
                                          'fontWeight': 'bold'})
                        ], className="text-center")
                    ], width=2),
                    
                    # Memory
                    dbc.Col([
                        html.Div([
                            html.Div("🧠 Mémoire", className="small text-muted"),
                            html.H4(f"{latest_metrics['memory']:.1f}%", 
                                   style={'color': 'red' if latest_metrics['memory'] > 85 else 'green',
                                          'fontWeight': 'bold'})
                        ], className="text-center")
                    ], width=2),
                    
                    # Disk
                    dbc.Col([
                        html.Div([
                            html.Div("💾 Disque", className="small text-muted"),
                            html.H4(f"{latest_metrics['disk']:.1f}%", 
                                   style={'color': 'red' if latest_metrics['disk'] > 90 else 'green',
                                          'fontWeight': 'bold'})
                        ], className="text-center")
                    ], width=2),
                    
                    # Network
                    dbc.Col([
                        html.Div([
                            html.Div("🌐 Réseau", className="small text-muted"),
                            html.H4(f"{latest_metrics['network']:.1f}MB", 
                                   style={'color': 'orange', 'fontWeight': 'bold'})
                        ], className="text-center")
                    ], width=2),
                    
                    # Alerts
                    dbc.Col([
                        html.Div([
                            html.Div("🚨 Alertes", className="small text-muted"),
                            html.H4(f"{len(df_alerts)}", 
                                   style={'color': 'red' if len(df_alerts) > 0 else 'green',
                                          'fontWeight': 'bold'})
                        ], className="text-center")
                    ], width=1),
                    
                    # Actions
                    dbc.Col([
                        html.Div([
                            html.Div("⚡ Actions", className="small text-muted"),
                            html.H4(f"{len(df_actions)}", 
                                   style={'color': 'blue', 'fontWeight': 'bold'})
                        ], className="text-center")
                    ], width=1),
                    
                    # Services
                    dbc.Col([
                        html.Div([
                            html.Div("🔧 Services", className="small text-muted"),
                            html.H4(f"{len(df_services['service'].unique()) if not df_services.empty else 0}", 
                                   style={'color': 'purple', 'fontWeight': 'bold'})
                        ], className="text-center")
                    ], width=1),
                    
                    # Last Update
                    dbc.Col([
                        html.Div([
                            html.Div("🕐 Dernière MAJ", className="small text-muted"),
                            html.H4(f"{datetime.now().strftime('%H:%M:%S')}", 
                                   style={'color': 'gray', 'fontWeight': 'bold'})
                        ], className="text-center")
                    ], width=1)
                ])
                
                live_metrics = metrics_row
            else:
                live_metrics = dbc.Alert("⏳ En attente de données de surveillance...", 
                                       color="warning", className="text-center")
            
            return (system_fig, alerts_service_fig, actions_fig, live_metrics, 
                   service_table, alerts_table, actions_table)
        
        return app
    
    def run_dashboard(self):
        """Lance le tableau de bord"""
        print(f"🚀 Démarrage du tableau de bord sur http://localhost:{self.port}")
        app = self.create_dashboard()
        app.run_server(debug=False, host='0.0.0.0', port=self.port)