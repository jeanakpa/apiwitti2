#!/usr/bin/env python3
"""
Script pour tester le démarrage de app.py et wsgi.py
"""

import os
import sys
import subprocess
import time

def test_app_startup():
    """Teste le démarrage de app.py"""
    print("🧪 Test du démarrage de app.py...")
    
    try:
        # Définir les variables d'environnement
        env = os.environ.copy()
        env['SECRET_KEY'] = 'test-secret-key'
        env['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
        env['DATABASE_URL'] = 'sqlite:///test.db'
        env['FLASK_ENV'] = 'development'
        
        # Démarrer app.py en arrière-plan
        process = subprocess.Popen(
            [sys.executable, 'app.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Attendre un peu pour voir s'il démarre
        time.sleep(3)
        
        # Vérifier si le processus est toujours en vie
        if process.poll() is None:
            print("✅ app.py a démarré avec succès")
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ app.py a échoué au démarrage:")
            print(f"   STDOUT: {stdout}")
            print(f"   STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test de app.py: {e}")
        return False

def test_wsgi_startup():
    """Teste le démarrage de wsgi.py"""
    print("\n🧪 Test du démarrage de wsgi.py...")
    
    try:
        # Définir les variables d'environnement
        env = os.environ.copy()
        env['SECRET_KEY'] = 'test-secret-key'
        env['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
        env['DATABASE_URL'] = 'sqlite:///test.db'
        env['FLASK_ENV'] = 'development'
        
        # Démarrer wsgi.py en arrière-plan
        process = subprocess.Popen(
            [sys.executable, 'wsgi.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Attendre un peu pour voir s'il démarre
        time.sleep(3)
        
        # Vérifier si le processus est toujours en vie
        if process.poll() is None:
            print("✅ wsgi.py a démarré avec succès")
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ wsgi.py a échoué au démarrage:")
            print(f"   STDOUT: {stdout}")
            print(f"   STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test de wsgi.py: {e}")
        return False

def test_gunicorn_wsgi():
    """Teste le démarrage avec Gunicorn"""
    print("\n🧪 Test du démarrage avec Gunicorn...")
    
    try:
        # Définir les variables d'environnement
        env = os.environ.copy()
        env['SECRET_KEY'] = 'test-secret-key'
        env['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
        env['DATABASE_URL'] = 'sqlite:///test.db'
        env['FLASK_ENV'] = 'development'
        
        # Démarrer Gunicorn avec wsgi.py
        process = subprocess.Popen(
            ['gunicorn', 'wsgi:app', '--bind', '127.0.0.1:8000', '--timeout', '30'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Attendre un peu pour voir s'il démarre
        time.sleep(5)
        
        # Vérifier si le processus est toujours en vie
        if process.poll() is None:
            print("✅ Gunicorn avec wsgi.py a démarré avec succès")
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Gunicorn avec wsgi.py a échoué au démarrage:")
            print(f"   STDOUT: {stdout}")
            print(f"   STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test de Gunicorn: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test de démarrage des applications")
    print("=" * 50)
    
    # Test des démarrages
    app_ok = test_app_startup()
    wsgi_ok = test_wsgi_startup()
    gunicorn_ok = test_gunicorn_wsgi()
    
    print("\n" + "=" * 50)
    print("📊 Résultats des tests:")
    print(f"   app.py: {'✅' if app_ok else '❌'}")
    print(f"   wsgi.py: {'✅' if wsgi_ok else '❌'}")
    print(f"   gunicorn wsgi:app: {'✅' if gunicorn_ok else '❌'}")
    
    if app_ok and wsgi_ok and gunicorn_ok:
        print("\n🎉 SUCCÈS: Tous les tests de démarrage sont passés !")
        print("✅ wsgi.py fonctionne exactement comme app.py")
        print("✅ Gunicorn peut démarrer avec wsgi:app")
        return 0
    else:
        print("\n❌ ÉCHEC: Certains tests de démarrage ont échoué")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 