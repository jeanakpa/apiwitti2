#!/usr/bin/env python3
"""
Script pour tester le déploiement localement
"""

import os
import sys

def test_imports():
    """Teste tous les imports nécessaires"""
    print("🧪 Test des imports...")
    
    try:
        # Test des imports de base
        from flask import Flask
        print("✅ Flask importé avec succès")
        
        from extensions import db, ma, jwt, migrate
        print("✅ Extensions importées avec succès")
        
        # Test des modèles
        from Models.mywitti_survey import MyWittiSurvey, MyWittiSurveyOption, MyWittiSurveyResponse
        print("✅ Modèles survey importés avec succès")
        
        from Models.mywitti_users import MyWittiUser
        print("✅ Modèle utilisateur importé avec succès")
        
        from Models.mywitti_client import MyWittiClient
        print("✅ Modèle client importé avec succès")
        
        from Models.mywitti_advertisement import MyWittiAdvertisement
        print("✅ Modèle publicité importé avec succès")
        
        # Test des blueprints
        from Account.views import accounts_bp
        print("✅ Blueprint Account importé avec succès")
        
        from Customer.views import customer_bp
        print("✅ Blueprint Customer importé avec succès")
        
        from Lot.views import lot_bp
        print("✅ Blueprint Lot importé avec succès")
        
        from Admin.views import admin_bp
        print("✅ Blueprint Admin importé avec succès")
        
        from Advertisement.views import advertisement_bp
        print("✅ Blueprint Advertisement importé avec succès")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def test_app_creation():
    """Teste la création de l'application Flask"""
    print("\n🧪 Test de création de l'application...")
    
    try:
        # Définir des variables d'environnement pour les tests
        os.environ['SECRET_KEY'] = 'test-secret-key'
        os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
        os.environ['DATABASE_URL'] = 'sqlite:///test.db'
        os.environ['FLASK_ENV'] = 'development'
        
        from app import create_app
        app = create_app('development')
        print("✅ Application Flask créée avec succès")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'application: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test de déploiement Witti Witti API")
    print("=" * 50)
    
    # Test des imports
    imports_ok = test_imports()
    
    # Test de création de l'app
    app_ok = test_app_creation()
    
    print("\n" + "=" * 50)
    if imports_ok and app_ok:
        print("🎉 Tous les tests sont passés ! L'application est prête pour le déploiement.")
        return 0
    else:
        print("❌ Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 