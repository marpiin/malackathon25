import bcrypt
import secrets
import string
from datetime import datetime, timedelta
import re
from flask import current_app

def hash_password(password):
    """Hashea una contraseña usando bcrypt con salt automático"""
    salt = bcrypt.gensalt(rounds=12)  # 12 rondas para seguridad
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, password_hash):
    """Verifica una contraseña contra su hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except:
        return False

def validate_password(password):
    """
    Valida que una contraseña cumpla los requisitos de seguridad
    Returns: (bool, str) - (es_valida, mensaje_error)
    """
    errors = []
    
    if len(password) < current_app.config['PASSWORD_MIN_LENGTH']:
        errors.append(f"Mínimo {current_app.config['PASSWORD_MIN_LENGTH']} caracteres")
    
    if current_app.config['PASSWORD_REQUIRE_UPPERCASE'] and not re.search(r'[A-Z]', password):
        errors.append("Al menos 1 letra mayúscula")
    
    if current_app.config['PASSWORD_REQUIRE_LOWERCASE'] and not re.search(r'[a-z]', password):
        errors.append("Al menos 1 letra minúscula")
    
    if current_app.config['PASSWORD_REQUIRE_DIGIT'] and not re.search(r'\d', password):
        errors.append("Al menos 1 número")
    
    if current_app.config['PASSWORD_REQUIRE_SPECIAL'] and not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=]', password):
        errors.append("Al menos 1 carácter especial (!@#$%...)")
    
    if errors:
        return False, "\n".join(errors)
    
    return True, "Contraseña válida"

def generate_verification_code(length=6):
    """
    Genera un código de verificación alfanumérico bonito
    Evita caracteres confusos: 0, O, I, 1, l
    """
    characters = string.ascii_uppercase + string.digits
    # Eliminar caracteres confusos
    characters = characters.replace('0', '').replace('O', '').replace('I', '').replace('1', '').replace('L', '')
    
    code = ''.join(secrets.choice(characters) for _ in range(length))
    return code

def validate_email(email):
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_code_expiration_time():
    """Retorna la fecha/hora de expiración del código"""
    minutes = current_app.config['CODE_EXPIRATION_MINUTES']
    return datetime.now() + timedelta(minutes=minutes)
