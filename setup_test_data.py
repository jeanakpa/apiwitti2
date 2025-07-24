#!/usr/bin/env python3
"""
Script pour configurer l'environnement et créer les données de test
"""
import os
import sys
from datetime import datetime, timedelta
import uuid

# Définir les variables d'environnement
os.environ['SECRET_KEY'] = 'your-secret-key-here-for-development-only'
os.environ['JWT_SECRET_KEY'] = 'your-jwt-secret-key-here-for-development-only'
os.environ['DATABASE_URL'] = 'postgresql://postgres:mywitti@localhost:5432/mywitti'
os.environ['CORS_ORIGINS'] = '*'
os.environ['FLASK_ENV'] = 'development'

# Ajouter le répertoire parent au path pour importer l'app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from Models.mywitti_users import MyWittiUser
from Models.mywitti_user_type import MyWittiUserType
from Models.mywitti_category import MyWittiCategory
from Models.mywitti_client import MyWittiClient
from Models.mywitti_lots import MyWittiLot
from Models.mywitti_jetons_transactions import MyWittiJetonsTransactions
from Models.mywitti_notification import MyWittiNotification
from Models.mywitti_faq import MyWittiFAQ
from Models.mywitti_survey import MyWittiSurvey, MyWittiSurveyOption
from werkzeug.security import generate_password_hash
from Models.mywitti_referral import MyWittiReferral

def create_test_data():
    """Crée toutes les données de test"""
    
    # Créer l'application
    app = create_app('development')
    
    with app.app_context():
        try:
            print("=== CRÉATION DES DONNÉES DE TEST ===")
            
            # 1. Créer les types d'utilisateurs
            print("1. Création des types d'utilisateurs...")
            user_types = [
                MyWittiUserType(
                    id=1,
                    type_name='superadmin',
                    description='Super administrateur avec tous les droits',
                    permissions={'all': True},
                    is_active=True
                ),
                MyWittiUserType(
                    id=2,
                    type_name='admin',
                    description='Administrateur avec droits limités',
                    permissions={'read': True, 'write': True, 'delete': False},
                    is_active=True
                ),
                MyWittiUserType(
                    id=3,
                    type_name='client',
                    description='Client standard',
                    permissions={'read_own': True, 'write_own': True},
                    is_active=True
                )
            ]
            
            for user_type in user_types:
                existing = MyWittiUserType.query.get(user_type.id)
                if not existing:
                    db.session.add(user_type)
                    print(f"   - Type '{user_type.type_name}' créé")
                else:
                    print(f"   - Type '{user_type.type_name}' existe déjà")
            
            # 2. Créer les catégories
            print("\n2. Création des catégories...")
            categories = [
                MyWittiCategory(
                    id=1,
                    category_name='Eco Premium',
                    slug='eco-premium',
                    description='Catégorie Eco Premium (1 à 99 jetons)',
                    categ_points=10,
                    recompense_point=5,
                    level=1,
                    min_jetons=1,
                    nb_jours=30
                ),
                MyWittiCategory(
                    id=2,
                    category_name='Executive',
                    slug='executive',
                    description='Catégorie Executive (100 à 999 jetons)',
                    categ_points=50,
                    recompense_point=25,
                    level=2,
                    min_jetons=100,
                    nb_jours=60
                ),
                MyWittiCategory(
                    id=3,
                    category_name='Executive +',
                    slug='executive-plus',
                    description='Catégorie Executive + (1000 à 3000 jetons)',
                    categ_points=100,
                    recompense_point=50,
                    level=3,
                    min_jetons=1000,
                    nb_jours=90
                ),
                MyWittiCategory(
                    id=4,
                    category_name='First Class',
                    slug='first-class',
                    description='Catégorie First Class (+ de 3000 jetons)',
                    categ_points=200,
                    recompense_point=100,
                    level=4,
                    min_jetons=3000,
                    nb_jours=120
                )
            ]
            
            for category in categories:
                existing = MyWittiCategory.query.get(category.id)
                if not existing:
                    db.session.add(category)
                    print(f"   - Catégorie '{category.category_name}' créée")
                else:
                    print(f"   - Catégorie '{category.category_name}' existe déjà")
            
            # 3. Créer l'utilisateur superadmin
            print("\n3. Création de l'utilisateur superadmin...")
            superadmin = MyWittiUser.query.filter_by(email='superadmin@gmail.com').first()
            if not superadmin:
                superadmin = MyWittiUser(
                    id=1,
                    user_id='superadmin',
                    password_hash=generate_password_hash('123456'),
                    first_name='Super',
                    last_name='Admin',
                    user_type='superadmin',
                    is_active=True,
                    is_admin=True,
                    is_superuser=True,
                    must_change_password=False,
                    user_type_id=1,
                    email='superadmin@gmail.com',
                    created_at=datetime.utcnow()
                )
                db.session.add(superadmin)
                print("   - Utilisateur superadmin créé")
            else:
                print("   - Utilisateur superadmin existe déjà")
            
            # 4. Créer l'utilisateur client de test
            print("\n4. Création de l'utilisateur client de test...")
            user_test = MyWittiUser.query.filter_by(email='user_test@gmail.com').first()
            if not user_test:
                user_test = MyWittiUser(
                    id=2,
                    user_id='user_test',
                    password_hash=generate_password_hash('123456'),
                    first_name='User',
                    last_name='Test',
                    user_type='client',
                    is_active=True,
                    is_admin=False,
                    is_superuser=False,
                    must_change_password=False,
                    user_type_id=3,
                    email='user_test@gmail.com',
                    created_at=datetime.utcnow()
                )
                db.session.add(user_test)
                print("   - Utilisateur user_test créé")
            else:
                print("   - Utilisateur user_test existe déjà")
            
            # 5. Créer le client associé à user_test
            print("\n5. Création du client associé...")
            client_test = MyWittiClient.query.filter_by(customer_code='user_test').first()
            if not client_test:
                client_test = MyWittiClient(
                    id=1,
                    customer_code='user_test',
                    short_name='Test',
                    first_name='User',
                    gender='M',
                    birth_date=datetime(1990, 1, 1),
                    phone_number='+22501234567',
                    street='123 Rue Test, Abidjan',
                    solde=500,
                    total=500,
                    date_ouverture=datetime(2025, 1, 1),
                    nombre_jours=30,
                    category_id=2,
                    user_id=2
                )
                db.session.add(client_test)
                print("   - Client user_test créé")
            else:
                print("   - Client user_test existe déjà")
            
            # 6. Créer quelques lots/récompenses
            print("\n6. Création des lots/récompenses...")
            lots = [
                MyWittiLot(
                    id=1,
                    libelle='Carte cadeau 5000 FCFA',
                    jetons=50,
                    stock=100,
                    category_id=1,
                    recompense_image='/static/uploads/gift-card.jpg',
                    created_at=datetime.utcnow()
                ),
                MyWittiLot(
                    id=2,
                    libelle='Carte cadeau 10000 FCFA',
                    jetons=100,
                    stock=50,
                    category_id=2,
                    recompense_image='/static/uploads/gift-card.jpg',
                    created_at=datetime.utcnow()
                ),
                MyWittiLot(
                    id=3,
                    libelle='Smartphone Samsung',
                    jetons=1500,
                    stock=10,
                    category_id=3,
                    recompense_image='/static/uploads/smartphone.jpg',
                    created_at=datetime.utcnow()
                ),
                MyWittiLot(
                    id=4,
                    libelle='Voyage à Paris',
                    jetons=5000,
                    stock=2,
                    category_id=4,
                    recompense_image='/static/uploads/paris.jpg',
                    created_at=datetime.utcnow()
                )
            ]
            
            for lot in lots:
                existing = MyWittiLot.query.get(lot.id)
                if not existing:
                    db.session.add(lot)
                    print(f"   - Lot '{lot.libelle}' créé")
                else:
                    print(f"   - Lot '{lot.libelle}' existe déjà")
            
            # 7. Créer quelques transactions
            print("\n7. Création des transactions...")
            transactions = [
                MyWittiJetonsTransactions(
                    id=1,
                    client_id=1,
                    lot_id=1,
                    montant=50,
                    motif='Achat carte cadeau',
                    date_transaction=datetime.now() - timedelta(days=5)
                ),
                MyWittiJetonsTransactions(
                    id=2,
                    client_id=1,
                    lot_id=2,
                    montant=100,
                    motif='Achat carte cadeau',
                    date_transaction=datetime.now() - timedelta(days=3)
                ),
                MyWittiJetonsTransactions(
                    id=3,
                    client_id=1,
                    lot_id=None,
                    montant=200,
                    motif='Bonus fidélité',
                    date_transaction=datetime.now() - timedelta(days=1)
                )
            ]
            
            for transaction in transactions:
                existing = MyWittiJetonsTransactions.query.get(transaction.id)
                if not existing:
                    db.session.add(transaction)
                    print(f"   - Transaction {transaction.id} créée")
                else:
                    print(f"   - Transaction {transaction.id} existe déjà")
            
            # 8. Créer quelques notifications de test
            print("\n8. Création des notifications de test...")
            notifications = [
                MyWittiNotification(
                    id=1,
                    user_id=2,
                    message='Bienvenue sur la plateforme MyWitti !',
                    created_at=datetime.now() - timedelta(days=7),
                    is_read=False
                ),
                MyWittiNotification(
                    id=2,
                    user_id=2,
                    message='Votre commande #123 a été validée',
                    created_at=datetime.now() - timedelta(days=2),
                    is_read=False
                ),
                MyWittiNotification(
                    id=3,
                    user_id=1,
                    message='Nouveau client inscrit : user_test',
                    created_at=datetime.now() - timedelta(days=1),
                    is_read=False
                )
            ]
            
            for notification in notifications:
                existing = MyWittiNotification.query.get(notification.id)
                if not existing:
                    db.session.add(notification)
                    print(f"   - Notification {notification.id} créée")
                else:
                    print(f"   - Notification {notification.id} existe déjà")
            
            # 9. Créer quelques FAQs de test
            print("\n9. Création des FAQs de test...")
            faqs = [
                MyWittiFAQ(
                    id=1,
                    question='Comment fonctionne le système de jetons ?',
                    answer='Les jetons sont des points que vous gagnez en utilisant nos services. Vous pouvez les échanger contre des récompenses.'
                ),
                MyWittiFAQ(
                    id=2,
                    question='Comment passer une commande ?',
                    answer='Allez dans la section "Lots" et sélectionnez l\'article de votre choix. Ajoutez-le au panier et validez votre commande.'
                ),
                MyWittiFAQ(
                    id=3,
                    question='Comment contacter le support ?',
                    answer='Vous pouvez nous contacter via l\'onglet "Support" ou par téléphone au +2250710922213.'
                )
            ]
            
            for faq in faqs:
                existing = MyWittiFAQ.query.get(faq.id)
                if not existing:
                    db.session.add(faq)
                    print(f"   - FAQ {faq.id} créée")
                else:
                    print(f"   - FAQ {faq.id} existe déjà")
            
            # 10. Créer un sondage de test
            print("\n10. Création du sondage de test...")
            survey = MyWittiSurvey.query.get(1)
            if not survey:
                survey = MyWittiSurvey(
                    id=1,
                    title='Satisfaction générale',
                    description='Comment évaluez-vous votre expérience sur notre plateforme ?',
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.session.add(survey)
                print("   - Sondage créé")
                
                # Créer les options du sondage
                options = [
                    MyWittiSurveyOption(survey_id=1, option_text='Très mal', option_value=1),
                    MyWittiSurveyOption(survey_id=1, option_text='Mal', option_value=2),
                    MyWittiSurveyOption(survey_id=1, option_text='Moyen', option_value=3),
                    MyWittiSurveyOption(survey_id=1, option_text='Bien', option_value=4),
                    MyWittiSurveyOption(survey_id=1, option_text='Très bien', option_value=5)
                ]
                
                for option in options:
                    db.session.add(option)
                print("   - Options du sondage créées")
            else:
                print("   - Sondage existe déjà")
            
            # 9. Créer quelques parrainages de test
            print("\n9. Création des parrainages de test...")
            referrals = [
                MyWittiReferral(
                    id=1,
                    referrer_id=1,  # superadmin
                    referred_email='ami1@example.com',
                    referral_code=str(uuid.uuid4())[:8],
                    status='pending',
                    created_at=datetime.utcnow() - timedelta(days=5)
                ),
                MyWittiReferral(
                    id=2,
                    referrer_id=1,  # superadmin
                    referred_email='ami2@example.com',
                    referral_code=str(uuid.uuid4())[:8],
                    status='accepted',
                    created_at=datetime.utcnow() - timedelta(days=3)
                ),
                MyWittiReferral(
                    id=3,
                    referrer_id=2,  # user_test
                    referred_email='ami3@example.com',
                    referral_code=str(uuid.uuid4())[:8],
                    status='rewarded',
                    created_at=datetime.utcnow() - timedelta(days=1)
                )
            ]
            
            for referral in referrals:
                existing = MyWittiReferral.query.get(referral.id)
                if not existing:
                    db.session.add(referral)
                    print(f"   - Parrainage {referral.id} créé")
                else:
                    print(f"   - Parrainage {referral.id} existe déjà")
            
            # Valider toutes les modifications
            db.session.commit()
            print("\n=== DONNÉES DE TEST CRÉÉES AVEC SUCCÈS ===")
            
            # Afficher un résumé
            print("\n=== RÉSUMÉ DES DONNÉES CRÉÉES ===")
            print(f"Types d'utilisateurs: {MyWittiUserType.query.count()}")
            print(f"Catégories: {MyWittiCategory.query.count()}")
            print(f"Utilisateurs: {MyWittiUser.query.count()}")
            print(f"Clients: {MyWittiClient.query.count()}")
            print(f"Lots: {MyWittiLot.query.count()}")
            print(f"Transactions: {MyWittiJetonsTransactions.query.count()}")
            print(f"Notifications: {MyWittiNotification.query.count()}")
            print(f"FAQs: {MyWittiFAQ.query.count()}")
            print(f"Sondages: {MyWittiSurvey.query.count()}")
            print(f"Options de sondage: {MyWittiSurveyOption.query.count()}")
            
            print("\n=== INFORMATIONS DE CONNEXION ===")
            print("Superadmin:")
            print("  Email: superadmin@gmail.com")
            print("  Mot de passe: 123456")
            print("\nClient de test:")
            print("  Email: user_test@gmail.com")
            print("  Mot de passe: 123456")
            
        except Exception as e:
            print(f"Erreur lors de la création des données de test: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    create_test_data() 