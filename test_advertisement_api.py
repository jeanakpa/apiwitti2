#!/usr/bin/env python3
"""
Script de test pour l'API des publicités
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:5000"
ADMIN_TOKEN = None  # À remplacer par un token admin valide

def get_admin_token():
    """Récupérer un token admin pour les tests"""
    global ADMIN_TOKEN
    
    if ADMIN_TOKEN:
        return ADMIN_TOKEN
    
    # Connexion admin (remplacer par les vraies credentials)
    login_data = {
        "user_id": "admin",  # Remplacer par l'ID admin réel
        "password": "password"  # Remplacer par le mot de passe admin réel
    }
    
    try:
        response = requests.post(f"{BASE_URL}/accounts/login", json=login_data)
        if response.status_code == 200:
            ADMIN_TOKEN = response.json().get("access_token")
            return ADMIN_TOKEN
        else:
            print(f"Erreur de connexion admin: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"Erreur lors de la connexion: {e}")
        return None

def test_create_advertisement():
    """Test de création d'une publicité"""
    print("\n=== Test de création d'une publicité ===")
    
    token = get_admin_token()
    if not token:
        print("Impossible d'obtenir le token admin")
        return False
    
    advertisement_data = {
        "title": "Test Promotion",
        "description": "Description de test pour la promotion",
        "image_url": "https://example.com/test-image.jpg",
        "country": "France",
        "is_active": True
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/advertisement/", 
                               json=advertisement_data, 
                               headers=headers)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            return response.json().get("id")
        else:
            return None
            
    except Exception as e:
        print(f"Erreur: {e}")
        return None

def test_get_advertisements():
    """Test de récupération des publicités"""
    print("\n=== Test de récupération des publicités ===")
    
    token = get_admin_token()
    if not token:
        print("Impossible d'obtenir le token admin")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/advertisement/", headers=headers)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def test_get_active_advertisements():
    """Test de récupération des publicités actives"""
    print("\n=== Test de récupération des publicités actives ===")
    
    try:
        response = requests.get(f"{BASE_URL}/advertisement/active")
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def test_update_advertisement(advertisement_id):
    """Test de modification d'une publicité"""
    print(f"\n=== Test de modification de la publicité {advertisement_id} ===")
    
    token = get_admin_token()
    if not token:
        print("Impossible d'obtenir le token admin")
        return False
    
    update_data = {
        "title": "Titre modifié",
        "description": "Description modifiée",
        "is_active": False
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/advertisement/{advertisement_id}", 
                              json=update_data, 
                              headers=headers)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def test_toggle_advertisement(advertisement_id):
    """Test de basculement du statut d'une publicité"""
    print(f"\n=== Test de basculement de la publicité {advertisement_id} ===")
    
    token = get_admin_token()
    if not token:
        print("Impossible d'obtenir le token admin")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/advertisement/toggle/{advertisement_id}", 
                               headers=headers)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def test_delete_advertisement(advertisement_id):
    """Test de suppression d'une publicité"""
    print(f"\n=== Test de suppression de la publicité {advertisement_id} ===")
    
    token = get_admin_token()
    if not token:
        print("Impossible d'obtenir le token admin")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{BASE_URL}/advertisement/{advertisement_id}", 
                                 headers=headers)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Erreur: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("=== Tests de l'API des publicités ===")
    
    # Test 1: Créer une publicité
    advertisement_id = test_create_advertisement()
    
    if advertisement_id:
        print(f"✅ Publicité créée avec l'ID: {advertisement_id}")
        
        # Test 2: Récupérer toutes les publicités
        if test_get_advertisements():
            print("✅ Récupération des publicités réussie")
        else:
            print("❌ Échec de la récupération des publicités")
        
        # Test 3: Récupérer les publicités actives
        if test_get_active_advertisements():
            print("✅ Récupération des publicités actives réussie")
        else:
            print("❌ Échec de la récupération des publicités actives")
        
        # Test 4: Modifier la publicité
        if test_update_advertisement(advertisement_id):
            print("✅ Modification de la publicité réussie")
        else:
            print("❌ Échec de la modification de la publicité")
        
        # Test 5: Basculement du statut
        if test_toggle_advertisement(advertisement_id):
            print("✅ Basculement du statut réussi")
        else:
            print("❌ Échec du basculement du statut")
        
        # Test 6: Supprimer la publicité
        if test_delete_advertisement(advertisement_id):
            print("✅ Suppression de la publicité réussie")
        else:
            print("❌ Échec de la suppression de la publicité")
    else:
        print("❌ Échec de la création de la publicité")
    
    print("\n=== Tests terminés ===")

if __name__ == "__main__":
    main() 