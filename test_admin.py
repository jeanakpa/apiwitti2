import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_admin_functionality():
    """Teste toutes les fonctionnalites admin"""
    
    # 1. Connexion admin
    login_response = requests.post(f"{BASE_URL}/accounts/admin/login", json={
        "email": "superadmin@gmail.com",
        "password": "123456"
    })
    
    if login_response.status_code != 200:
        print(f"Erreur de login admin: {login_response.status_code}")
        return
    
    admin_token = login_response.json().get("access_token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    print("Connexion admin reussie")
    
    # 2. Test des statistiques
    print("\n=== TEST STATISTIQUES ===")
    stats_response = requests.get(f"{BASE_URL}/admin/stats", headers=admin_headers)
    print(f"Stats - Status: {stats_response.status_code}")
    if stats_response.status_code == 200:
        stats_data = stats_response.json()
        print(f"Stats - Clients totaux: {stats_data.get('total_customers')}")
        print(f"Stats - Meilleur client: {stats_data.get('top_customer_tokens')}")
        print(f"Stats - Commandes en attente: {stats_data.get('pending_orders')}")
        print(f"Stats - Commandes validees: {stats_data.get('validated_orders')}")
    else:
        print(f"Erreur stats: {stats_response.text}")
    
    # 3. Test de la liste des clients
    print("\n=== TEST LISTE CLIENTS ===")
    customers_response = requests.get(f"{BASE_URL}/admin/customers", headers=admin_headers)
    print(f"Customers - Status: {customers_response.status_code}")
    if customers_response.status_code == 200:
        customers_data = customers_response.json()
        print(f"Customers - Nombre de clients: {len(customers_data)}")
        for customer in customers_data[:3]:
            print(f"  - {customer.get('customer_code')}: {customer.get('first_name')} {customer.get('short_name')} ({customer.get('jetons')} jetons)")
    else:
        print(f"Erreur customers: {customers_response.text}")
    
    # 4. Test de la liste des commandes
    print("\n=== TEST LISTE COMMANDES ===")
    orders_response = requests.get(f"{BASE_URL}/admin/orders", headers=admin_headers)
    print(f"Orders - Status: {orders_response.status_code}")
    if orders_response.status_code == 200:
        orders_data = orders_response.json()
        print(f"Orders - Nombre de commandes: {len(orders_data.get('orders', []))}")
        for order in orders_data.get('orders', [])[:3]:
            print(f"  - Commande {order.get('id')}: {order.get('status')} - {order.get('amount')} jetons")
    else:
        print(f"Erreur orders: {orders_response.text}")
    
    # 5. Test de la gestion du stock
    print("\n=== TEST GESTION STOCK ===")
    stock_response = requests.get(f"{BASE_URL}/admin/stock", headers=admin_headers)
    print(f"Stock - Status: {stock_response.status_code}")
    if stock_response.status_code == 200:
        stock_data = stock_response.json()
        print(f"Stock - Nombre d'articles: {len(stock_data)}")
        for item in stock_data[:3]:
            print(f"  - {item.get('libelle')}: {item.get('stock')} en stock")
    else:
        print(f"Erreur stock: {stock_response.text}")
    
    # 6. Test de la gestion des sondages
    print("\n=== TEST GESTION SONDAGES ===")
    surveys_response = requests.get(f"{BASE_URL}/admin/surveys", headers=admin_headers)
    print(f"Surveys - Status: {surveys_response.status_code}")
    if surveys_response.status_code == 200:
        surveys_data = surveys_response.json()
        print(f"Surveys - Nombre de sondages: {len(surveys_data)}")
        for survey in surveys_data[:3]:
            print(f"  - {survey.get('title')}: {len(survey.get('options', []))} options")
    else:
        print(f"Erreur surveys: {surveys_response.text}")
    
    # 7. Test de la gestion des notifications
    print("\n=== TEST GESTION NOTIFICATIONS ===")
    notifications_response = requests.get(f"{BASE_URL}/admin/notifications", headers=admin_headers)
    print(f"Notifications - Status: {notifications_response.status_code}")
    if notifications_response.status_code == 200:
        notifications_data = notifications_response.json()
        print(f"Notifications - Nombre de notifications: {len(notifications_data.get('notifications', []))}")
        for notif in notifications_data.get('notifications', [])[:3]:
            print(f"  - {notif.get('message')[:50]}...")
    else:
        print(f"Erreur notifications: {notifications_response.text}")
    
    print("\n=== FIN DES TESTS ADMIN ===")

if __name__ == "__main__":
    test_admin_functionality() 