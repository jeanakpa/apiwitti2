#!/usr/bin/env python3
"""
Script de test pour vérifier la connexion et l'authentification
"""
import os
import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:5000"

def test_connection():
    """Test de connexion à l'API"""
    try:
        response = requests.get(f"{BASE_URL}/faq", timeout=5)
        print(f"Test de connexion: {response.status_code}")
        print(f"Réponse: {response.text}")
        return True
    except Exception as e:
        print(f"Erreur de connexion: {e}")
        return False

def test_login(identifiant, password):
    """Test de connexion utilisateur"""
    try:
        data = {
            "identifiant": identifiant,
            "password": password
        }
        
        response = requests.post(
            f"{BASE_URL}/accounts/login",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Test de login pour {identifiant}:")
        print(f"Status: {response.status_code}")
        print(f"Réponse: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("access_token"):
                print("✅ Connexion réussie!")
                return result["access_token"]
            else:
                print("❌ Token d'accès manquant")
                return None
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors du login: {e}")
        return None

def test_admin_login(email, password):
    """Test de connexion admin"""
    try:
        data = {
            "email": email,
            "password": password
        }
        
        response = requests.post(
            f"{BASE_URL}/accounts/admin/login",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Test de login admin pour {email}:")
        print(f"Status: {response.status_code}")
        print(f"Réponse: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("access_token"):
                print("✅ Connexion admin réussie!")
                return result["access_token"]
            else:
                print("❌ Token d'accès manquant")
                return None
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors du login admin: {e}")
        return None

def test_protected_endpoint(token):
    """Test d'un endpoint protégé"""
    if not token:
        print("❌ Pas de token, impossible de tester l'endpoint protégé")
        return
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{BASE_URL}/customer/user_test/dashboard",
            headers=headers,
            timeout=10
        )
        
        print(f"Test endpoint protégé:")
        print(f"Status: {response.status_code}")
        print(f"Réponse: {response.text}")
        
    except Exception as e:
        print(f"❌ Erreur endpoint protégé: {e}")

if __name__ == "__main__":
    print("=== TEST DE L'API MYWITTI ===")
    
    # Test de connexion
    if not test_connection():
        print("❌ Impossible de se connecter à l'API")
        exit(1)
    
    print("\n=== TEST DE CONNEXION UTILISATEUR ===")
    
    # Test avec superadmin (utilise user_id)
    token = test_login("superadmin", "123456")
    
    if token:
        print("\n=== TEST ENDPOINT PROTÉGÉ ===")
        test_protected_endpoint(token)
    
    print("\n=== TEST AVEC CLIENT ===")
    test_login("user_test", "123456")
    
    print("\n=== TEST LOGIN ADMIN ===")
    test_admin_login("superadmin@gmail.com", "123456") 