import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def get_token(identifiant, password):
    """Récupère un token d'authentification"""
    response = requests.post(f"{BASE_URL}/accounts/login", json={
        "identifiant": identifiant,
        "password": password
    })
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def test_profile(token, customer_code):
    """Teste l'endpoint profile"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/customer/{customer_code}/profile", headers=headers)
    print(f"Profile {customer_code}:")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_transactions(token, customer_code):
    """Teste l'endpoint transactions"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/customer/{customer_code}/transactions?period=month", headers=headers)
    print(f"Transactions {customer_code}:")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_dashboard(token, customer_code):
    """Teste l'endpoint dashboard"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/customer/{customer_code}/dashboard", headers=headers)
    print(f"Dashboard {customer_code}:")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_cart(token):
    """Teste l'endpoint cart"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/lot/cart", headers=headers)
    print("Cart:")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_place_order(token):
    """Teste l'endpoint place-order"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/lot/place-order", headers=headers)
    print("Place Order:")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

if __name__ == "__main__":
    print("=== TEST DES ENDPOINTS CORRIGÉS ===\n")
    
    # Récupération du token pour user_test
    token = get_token("user_test", "123456")
    if not token:
        print("❌ Impossible de récupérer le token")
        exit(1)
    
    print("✅ Token récupéré avec succès\n")
    
    # Tests des endpoints
    test_profile(token, "user_test")
    test_transactions(token, "user_test")
    test_dashboard(token, "user_test")
    test_cart(token)
    test_place_order(token)
    
    print("=== FIN DES TESTS ===") 