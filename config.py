import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-por-defecto'
    
    # Credenciales de login
    LOGIN_USERNAME = os.environ.get('LOGIN_USERNAME')
    LOGIN_PASSWORD = os.environ.get('LOGIN_PASSWORD')
    
    # Base de datos
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_DSN = os.environ.get('DB_DSN')
    
    # Wallet config
    WALLET_LOCATION = os.environ.get('WALLET_LOCATION')
    WALLET_PASSWORD = os.environ.get('WALLET_PASSWORD')
    
    # Google Gemini API
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
