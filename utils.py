import re
import logging
from functools import wraps
from flask import current_app
from flask_restx import api
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

def validate_email(email):
    """Valide le format d'un email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Valide le format d'un numéro de téléphone"""
    phone_clean = re.sub(r'[\s\-\(\)\+]', '', phone)
    return len(phone_clean) >= 8 and phone_clean.isdigit()

def validate_required_fields(data, required_fields):
    """Valide que tous les champs requis sont présents"""
    missing_fields = []
    for field in required_fields:
        if not data.get(field):
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Champs requis manquants: {', '.join(missing_fields)}")
    
    return True

def sanitize_string(value, max_length=255):
    """Nettoie et valide une chaîne de caractères"""
    if not isinstance(value, str):
        raise ValueError("La valeur doit être une chaîne de caractères")
    
    sanitized = re.sub(r'[<>"\']', '', value.strip())
    
    if len(sanitized) > max_length:
        raise ValueError(f"La chaîne ne peut pas dépasser {max_length} caractères")
    
    return sanitized

def handle_api_error(func):
    """Décorateur pour gérer les erreurs de manière cohérente"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            current_app.logger.warning(f"Validation error in {func.__name__}: {str(e)}")
            return {"error": str(e)}, 400
        except IntegrityError as e:
            current_app.logger.error(f"Database integrity error in {func.__name__}: {str(e)}")
            return {"error": "Erreur de contrainte de base de données"}, 400
        except SQLAlchemyError as e:
            current_app.logger.error(f"Database error in {func.__name__}: {str(e)}")
            return {"error": "Erreur de base de données"}, 500
        except HTTPException as e:
            current_app.logger.error(f"HTTP error in {func.__name__}: {str(e)}")
            return {"error": str(e)}, e.code
        except Exception as e:
            current_app.logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            return {"error": "Erreur interne du serveur"}, 500
    return wrapper

def success_response(data=None, message="Opération réussie", status_code=200):
    """Format de réponse standard pour les succès"""
    response = {"message": message}
    if data is not None:
        response["data"] = data
    return response, status_code

def error_response(message="Erreur", status_code=400, details=None):
    """Format de réponse standard pour les erreurs"""
    response = {"error": message}
    if details:
        response["details"] = details
    return response, status_code 