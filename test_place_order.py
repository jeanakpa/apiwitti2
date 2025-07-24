import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_place_order():
    """Teste spécifiquement l'endpoint place-order avec ajout au panier"""
    
    # 1. Récupération du token
    login_response = requests.post(f"{BASE_URL}/accounts/login", json={
        "identifiant": "user_test",
        "password": "123456"
    })
    
    if login_response.status_code != 200:
        print(f"❌ Erreur de login: {login_response.status_code}")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Token récupéré")
    
    # 2. Vérification du panier initial
    cart_response = requests.get(f"{BASE_URL}/lot/cart", headers=headers)
    print(f"Panier initial - Status: {cart_response.status_code}")
    if cart_response.status_code == 200:
        cart_data = cart_response.json()
        print(f"Panier initial - Jetons requis: {cart_data.get('jetons_requis')}")
        print(f"Panier initial - Articles: {len(cart_data.get('transactions', []))}")
    
    # 3. Ajout d'un article au panier si le panier est vide
    if cart_data.get('jetons_requis', 0) == 0:
        print("\n=== AJOUT AU PANIER ===")
        add_to_cart_response = requests.post(f"{BASE_URL}/lot/cart", 
            headers=headers,
            json={"reward_id": 1, "quantity": 1}
        )
        print(f"Add to Cart - Status: {add_to_cart_response.status_code}")
        
        if add_to_cart_response.status_code == 200:
            print("✅ Article ajouté au panier")
            print(f"Réponse: {json.dumps(add_to_cart_response.json(), indent=2)}")
        else:
            print("❌ Erreur lors de l'ajout au panier")
            try:
                error_data = add_to_cart_response.json()
                print(f"Erreur: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Erreur: {add_to_cart_response.text}")
            return
    
    # 4. Vérification du panier après ajout
    cart_response = requests.get(f"{BASE_URL}/lot/cart", headers=headers)
    print(f"\nPanier après ajout - Status: {cart_response.status_code}")
    if cart_response.status_code == 200:
        cart_data = cart_response.json()
        print(f"Panier après ajout - Jetons requis: {cart_data.get('jetons_requis')}")
        print(f"Panier après ajout - Articles: {len(cart_data.get('transactions', []))}")
    
    # 5. Test place-order
    print("\n=== TEST PLACE-ORDER ===")
    place_order_response = requests.post(f"{BASE_URL}/lot/place-order", headers=headers)
    print(f"Place Order - Status: {place_order_response.status_code}")
    
    if place_order_response.status_code == 200:
        print("✅ Commande passée avec succès!")
        print(f"Réponse: {json.dumps(place_order_response.json(), indent=2)}")
    else:
        print("❌ Erreur lors de la commande")
        try:
            error_data = place_order_response.json()
            print(f"Erreur: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Erreur: {place_order_response.text}")

if __name__ == "__main__":
    test_place_order() 