#!/usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from Models.mywitti_comptes import MyWittiCompte
    print("✅ Import de MyWittiCompte réussi")
    print(f"Classe: {MyWittiCompte}")
    print(f"Table: {MyWittiCompte.__tablename__}")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
except Exception as e:
    print(f"❌ Erreur inattendue: {e}")

try:
    from Models.mywitti_client import MyWittiClient
    print("✅ Import de MyWittiClient réussi")
except ImportError as e:
    print(f"❌ Erreur d'import MyWittiClient: {e}")

try:
    from Models.mywitti_users import MyWittiUser
    print("✅ Import de MyWittiUser réussi")
except ImportError as e:
    print(f"❌ Erreur d'import MyWittiUser: {e}") 