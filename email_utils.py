from flask_mail import Mail, Message
from datetime import datetime

mail = Mail()

def send_verification_code_email(user_email, user_name, code):
    """Envía email con código de verificación"""
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #f5f5f5; }}
            .header {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                padding: 40px 20px; 
                text-align: center; 
                border-radius: 10px 10px 0 0; 
            }}
            .header h1 {{ margin: 0; font-size: 28px; }}
            .content {{ 
                background: white; 
                padding: 40px 30px; 
                border-radius: 0 0 10px 10px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .code-box {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                text-align: center;
                border-radius: 10px;
                margin: 30px 0;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            }}
            .code {{ 
                font-size: 36px; 
                font-weight: bold; 
                letter-spacing: 8px; 
                font-family: 'Courier New', monospace;
                display: inline-block;
                padding: 10px 20px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 8px;
            }}
            .warning {{ 
                background: #fff3cd; 
                border-left: 4px solid #ffc107; 
                padding: 15px; 
                margin: 20px 0; 
                border-radius: 4px;
            }}
            .footer {{ 
                text-align: center; 
                padding: 20px; 
                color: #999; 
                font-size: 12px; 
            }}
            .icon {{ font-size: 48px; margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="icon">🧠</div>
                <h1>Salud Mental Dashboard</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Verificación de Cuenta</p>
            </div>
            <div class="content">
                <h2 style="color: #667eea; margin-top: 0;">¡Hola {user_name}! 👋</h2>
                <p>Gracias por registrarte en nuestro Dashboard de Análisis de Salud Mental.</p>
                <p><strong>Tu código de verificación es:</strong></p>
                
                <div class="code-box">
                    <div style="font-size: 14px; margin-bottom: 10px; opacity: 0.9;">Código de verificación</div>
                    <div class="code">{code}</div>
                    <div style="font-size: 12px; margin-top: 10px; opacity: 0.8;">Expira en 10 minutos</div>
                </div>
                
                <p>Introduce este código en la página de verificación para activar tu cuenta.</p>
                
                <div class="warning">
                    <strong>⚠️ Importante:</strong>
                    <ul style="margin: 5px 0;">
                        <li>Este código es válido solo por <strong>10 minutos</strong></li>
                        <li>No compartas este código con nadie</li>
                        <li>Si no solicitaste este registro, ignora este email</li>
                    </ul>
                </div>
                
                <p style="color: #666; font-size: 14px; margin-top: 30px;">
                    Si tienes problemas, puedes solicitar un nuevo código desde la página de verificación.
                </p>
            </div>
            <div class="footer">
                <p>Salud Mental Dashboard - Malackathon 2025</p>
                <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg = Message(
        subject=f"🔐 Tu código de verificación: {code}",
        recipients=[user_email],
        html=html_body
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error al enviar email: {e}")
        return False

def send_welcome_email(user_email, user_name):
    """Envía email de bienvenida después de verificar"""
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; background: #f5f5f5; }}
            .header {{ 
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                color: white; 
                padding: 40px 20px; 
                text-align: center; 
                border-radius: 10px 10px 0 0; 
            }}
            .content {{ 
                background: white; 
                padding: 40px 30px; 
                border-radius: 0 0 10px 10px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .feature {{ 
                padding: 15px; 
                margin: 10px 0; 
                background: #f8f9fa; 
                border-left: 4px solid #667eea; 
                border-radius: 4px;
            }}
            .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div style="font-size: 64px;">🎉</div>
                <h1>¡Cuenta Verificada!</h1>
            </div>
            <div class="content">
                <h2 style="color: #28a745;">¡Bienvenido {user_name}!</h2>
                <p>Tu cuenta ha sido <strong>verificada exitosamente</strong>. Ya puedes acceder a todas las funcionalidades del Dashboard.</p>
                
                <h3 style="color: #667eea;">¿Qué puedes hacer ahora?</h3>
                
                <div class="feature">
                    📊 <strong>Análisis de Datos</strong><br>
                    <small>Explora datos de salud mental de diferentes comunidades</small>
                </div>
                
                <div class="feature">
                    📈 <strong>Visualizaciones</strong><br>
                    <small>Gráficos interactivos y estadísticas en tiempo real</small>
                </div>
                
                <div class="feature">
                    🗂️ <strong>Tablas de Datos</strong><br>
                    <small>Consulta información detallada con filtros avanzados</small>
                </div>
                
                <div class="feature">
                    🔍 <strong>Filtros Personalizados</strong><br>
                    <small>Filtra por comunidad, categoría, fechas y más</small>
                </div>
                
                <p style="margin-top: 30px;">¡Gracias por unirte a nosotros y contribuir al análisis de la salud mental!</p>
            </div>
            <div class="footer">
                <p>Salud Mental Dashboard - Malackathon 2025</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg = Message(
        subject="🎉 ¡Bienvenido a Salud Mental Dashboard!",
        recipients=[user_email],
        html=html_body
    )
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error al enviar email de bienvenida: {e}")
        return False
