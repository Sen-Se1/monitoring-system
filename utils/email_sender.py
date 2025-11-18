import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List

class EmailSender:
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.last_sent = {}
        
    def send_alert_email(self, recipients: List[str], subject: str, message: str, alert_type: str = "general") -> bool:
        """
        Envoie un email d'alerte aux destinataires
        Retourne True si l'email a été envoyé, False en cas d'erreur
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = f"🚨 Alerte Surveillance - {subject}"
            
            # Corps du message
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .alert {{ border-left: 4px solid #ff6b6b; padding: 15px; background-color: #fff5f5; }}
                    .info {{ border-left: 4px solid #4fc3f7; padding: 15px; background-color: #f0fdff; }}
                    .success {{ border-left: 4px solid #66bb6a; padding: 15px; background-color: #f1f8e9; }}
                    .header {{ color: #d32f2f; font-size: 18px; font-weight: bold; }}
                    .timestamp {{ color: #666; font-size: 12px; }}
                    .details {{ margin-top: 10px; }}
                </style>
            </head>
            <body>
                <div class="alert">
                    <div class="header">🚨 Alerte Système</div>
                    <div class="details">
                        {message.replace('\n', '<br>')}
                    </div>
                </div>
                <br>
                <div class="info">
                    <strong>Système de Surveillance Automatique</strong><br>
                    Cet email a été envoyé automatiquement par le système de surveillance.
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html_content, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✅ Email d'alerte envoyé à {len(recipients)} destinataire(s)")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'envoi de l'email: {e}")
            return False
    
    def can_send_alert(self, alert_type: str, cooldown_seconds: int) -> bool:
        """
        Vérifie si on peut envoyer une alerte du même type (éviter le spam)
        """
        now = datetime.now()
        last_sent = self.last_sent.get(alert_type)
        
        if last_sent is None:
            self.last_sent[alert_type] = now
            return True
        
        time_since_last = (now - last_sent).total_seconds()
        if time_since_last >= cooldown_seconds:
            self.last_sent[alert_type] = now
            return True
        
        return False