#!/usr/bin/env python3
"""
Script pour tester que wsgi.py et app.py fonctionnent identiquement
"""

import os
import sys

def test_app_import():
    """Teste l'import de l'application depuis app.py"""
    print("🧪 Test de l'import depuis app.py...")
    
    try:
        # Définir des variables d'environnement pour les tests
        os.environ['SECRET_KEY'] = 'test-secret-key'
        os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
        os.environ['DATABASE_URL'] = 'sqlite:///test.db'
        os.environ['FLASK_ENV'] = 'development'
        
        from app import app
        print("✅ Application importée depuis app.py avec succès")
        
        # Vérifier que l'app a tous les blueprints
        blueprints = list(app.blueprints.keys())
        expected_blueprints = ['accounts', 'customer', 'lot', 'admin', 'faq', 'support', 'survey', 'advertisement']
        
        print(f"📋 Blueprints trouvés: {blueprints}")
        print(f"📋 Blueprints attendus: {expected_blueprints}")
        
        for bp in expected_blueprints:
            if bp in blueprints:
                print(f"✅ Blueprint '{bp}' présent")
            else:
                print(f"❌ Blueprint '{bp}' manquant")
        
        return app
        
    except Exception as e:
        print(f"❌ Erreur lors de l'import depuis app.py: {e}")
        return None

def test_wsgi_import():
    """Teste l'import de l'application depuis wsgi.py"""
    print("\n🧪 Test de l'import depuis wsgi.py...")
    
    try:
        # Définir des variables d'environnement pour les tests
        os.environ['SECRET_KEY'] = 'test-secret-key'
        os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
        os.environ['DATABASE_URL'] = 'sqlite:///test.db'
        os.environ['FLASK_ENV'] = 'development'
        
        # Importer depuis wsgi.py
        from wsgi import app
        print("✅ Application importée depuis wsgi.py avec succès")
        
        # Vérifier que l'app a tous les blueprints
        blueprints = list(app.blueprints.keys())
        expected_blueprints = ['accounts', 'customer', 'lot', 'admin', 'faq', 'support', 'survey', 'advertisement']
        
        print(f"📋 Blueprints trouvés: {blueprints}")
        print(f"📋 Blueprints attendus: {expected_blueprints}")
        
        for bp in expected_blueprints:
            if bp in blueprints:
                print(f"✅ Blueprint '{bp}' présent")
            else:
                print(f"❌ Blueprint '{bp}' manquant")
        
        return app
        
    except Exception as e:
        print(f"❌ Erreur lors de l'import depuis wsgi.py: {e}")
        return None

def compare_apps(app1, app2):
    """Compare deux applications Flask"""
    print("\n🔍 Comparaison des applications...")
    
    if app1 is None or app2 is None:
        print("❌ Impossible de comparer - une des applications est None")
        return False
    
    # Comparer les blueprints
    blueprints1 = set(app1.blueprints.keys())
    blueprints2 = set(app2.blueprints.keys())
    
    if blueprints1 == blueprints2:
        print("✅ Les blueprints sont identiques")
    else:
        print(f"❌ Différence dans les blueprints:")
        print(f"   app.py: {blueprints1}")
        print(f"   wsgi.py: {blueprints2}")
        return False
    
    # Comparer les routes
    routes1 = set([rule.rule for rule in app1.url_map.iter_rules()])
    routes2 = set([rule.rule for rule in app2.url_map.iter_rules()])
    
    if routes1 == routes2:
        print("✅ Les routes sont identiques")
    else:
        print(f"❌ Différence dans les routes:")
        print(f"   app.py: {len(routes1)} routes")
        print(f"   wsgi.py: {len(routes2)} routes")
        return False
    
    # Comparer la configuration
    if app1.config == app2.config:
        print("✅ La configuration est identique")
    else:
        print("❌ Différence dans la configuration")
        return False
    
    print("🎉 Les applications sont identiques !")
    return True

def main():
    """Fonction principale de test"""
    print("🚀 Test de comparaison wsgi.py vs app.py")
    print("=" * 60)
    
    # Test des imports
    app_from_app = test_app_import()
    app_from_wsgi = test_wsgi_import()
    
    # Comparaison
    if app_from_app and app_from_wsgi:
        success = compare_apps(app_from_app, app_from_wsgi)
        if success:
            print("\n🎉 SUCCÈS: wsgi.py et app.py fonctionnent identiquement !")
            print("✅ Vous pouvez utiliser gunicorn wsgi:app pour le déploiement")
            return 0
        else:
            print("\n❌ ÉCHEC: Les applications ne sont pas identiques")
            return 1
    else:
        print("\n❌ ÉCHEC: Impossible d'importer une des applications")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 