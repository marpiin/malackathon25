import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    # Clave secreta
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-por-defecto'
    
    # Credenciales de login (mantener compatibilidad con sistema antiguo)
    LOGIN_USERNAME = os.environ.get('LOGIN_USERNAME')
    LOGIN_PASSWORD = os.environ.get('LOGIN_PASSWORD')
    
    # Base de datos Oracle
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_DSN = os.environ.get('DB_DSN')
    
    # Wallet config
    WALLET_LOCATION = os.environ.get('WALLET_LOCATION')
    WALLET_PASSWORD = os.environ.get('WALLET_PASSWORD')
    
    # Google Gemini API
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    
    # ========== NUEVAS CONFIGURACIONES PARA SISTEMA DE USUARIOS ==========
    
    # Configuración de Email (Gmail)
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Añadir a tu .env
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # Añadir a tu .env (App Password de Gmail)
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    
    # Validación de contraseñas
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGIT = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    # URL base (IMPORTANTE: usar tu dominio en producción)
    BASE_URL = os.environ.get('BASE_URL', 'https://vulnai.es')  # Cambia localhost por tu dominio
    
    # Verificación por código
    CODE_LENGTH = 6  # Longitud del código (ej: A3B7K9)
    CODE_EXPIRATION_MINUTES = 10  # El código expira en 10 minutos
