#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# Ajouter le répertoire courant au path Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test d'import des modèles
    print("=== Test des imports ===")
    from Models.mywitti_comptes import MyWittiCompte
    print("✅ MyWittiCompte importé")
    
    from Models.mywitti_client import MyWittiClient
    print("✅ MyWittiClient importé")
    
    from Models.mywitti_users import MyWittiUser
    print("✅ MyWittiUser importé")
    
    # Test d'import de la ressource
    print("\n=== Test d'import de la ressource ===")
    from Admin.resources.customer import CustomerList
    print("✅ CustomerList importé")
    
    # Test de création d'instance
    print("\n=== Test de création d'instance ===")
    customer_list = CustomerList()
    print("✅ Instance CustomerList créée")
    
    print("\n✅ Tous les tests sont passés avec succès!")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc() 