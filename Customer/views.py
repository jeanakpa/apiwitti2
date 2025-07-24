from flask import Blueprint, current_app, request
from flask_restx import Api, Resource, fields
import uuid
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from Models.mywitti_client import MyWittiClient
from Models.mywitti_category import MyWittiCategory
from Models.mywitti_jetons_transactions import MyWittiJetonsTransactions
from Models.mywitti_users import MyWittiUser
from Models.token_blacklist import TokenBlacklist
from extensions import db
from datetime import datetime, timedelta
from Models.mywitti_referral import MyWittiReferral
from Models.mywitti_notification import MyWittiNotification


customer_bp = Blueprint('customer', __name__)
reward_bp = Blueprint('reward', __name__)
api = Api(customer_bp, version='1.0', title='Customer API', description='API for customer operations')

# Define category ranges
CATEGORIES = [
    {"name": "Eco Premium", "code": "A", "min": 0, "max": 100},
    {"name": "Executive", "code": "B", "min": 100, "max": 1000},
    {"name": "Executive +", "code": "C", "min": 1000, "max": 3000},
    {"name": "First Class", "code": "D", "min": 3000, "max": float('inf')}
]

# Define response models for dashboard
dashboard_model = api.model('Dashboard', {
    'category': fields.String(description='Customer category'),
    'jetons': fields.Integer(description='Total jetons'),
    'percentage': fields.Float(description='Percentage within category range'),
    'short_name': fields.String(description='Short name'),
    'tokens_to_next_tier': fields.Integer(description='Jetons needed to reach next tier'),
    'last_transactions': fields.List(fields.Raw, description='Last 5 transactions')
})

# Define response models for transactions
transaction_model = api.model('Transaction', {
    'date': fields.String(description='Transaction date'),
    'amount': fields.String(description='Amount'),
    'type': fields.String(description='Transaction type (DEPOSIT/WITHDRAWAL)')
})

trends_model = api.model('Trends', {
    'deposit_percentage': fields.Float(description='Percentage of deposit transactions'),
    'withdrawal_percentage': fields.Float(description='Percentage of withdrawal transactions')
})

transactions_response_model = api.model('TransactionsResponse', {
    'transactions': fields.List(fields.Nested(transaction_model), description='List of transactions'),
    'total_transactions': fields.Integer(description='Total number of transactions'),
    'period_start': fields.String(description='Start of the period'),
    'period_end': fields.String(description='End of the period'),
    'trends': fields.Nested(trends_model, description='Transaction trends (deposit and withdrawal percentages)')
})

# Define response model for notifications
notification_model = api.model('Notification', {
    'id': fields.Integer(description='Notification ID'),
    'message': fields.String(description='Notification message'),
    'created_at': fields.String(description='Creation date')
})

notifications_response_model = api.model('NotificationsResponse', {
    'msg': fields.String(description='Success message'),
    'notifications': fields.List(fields.Nested(notification_model), description='List of notifications')
})

# Define response model for profile
profile_model = api.model('Profile', {
    'first_name': fields.String(description='Customer first name'),
    'short_name': fields.String(description='Customer short name'),
    'agency': fields.String(description='Customer agency'),
    'jetons': fields.Integer(description='Total jetons'),
    'category': fields.String(description='Customer category'),
    'percentage': fields.Float(description='Percentage within category range'),
    'tokens_to_next_tier': fields.Integer(description='Jetons needed to reach next tier')
})

#Invitation de parrainage
referral_model = api.model('Referral', {
    'referral_link': fields.String(description='Lien de parrainage'),
    'referred_email': fields.String(description='Email de l\'ami invité'),
    'status': fields.String(description='Statut du parrainage'),
    'created_at': fields.DateTime(description='Date de création')
})

# Define response model for logout
logout_response_model = api.model('LogoutResponse', {
    'msg': fields.String(description='Logout message')
})

@api.route('/dashboard')
class CustomerDashboard(Resource):
    @jwt_required()
    @api.marshal_with(dashboard_model)
    def get(self):
        try:
            identifiant = get_jwt_identity()
            current_app.logger.info(f"JWT Identity: {identifiant}")

            # Récupération sécurisée du client avec le customer_code issu du JWT
            customer = db.session.query(MyWittiClient).filter_by(customer_code=identifiant).first()
            if not customer:
                current_app.logger.warning(f"No customer found for identifiant/customer_code: {identifiant}")
                return {"message": "Customer not found"}, 404

            current_app.logger.info(f"Customer found: ID={customer.id}, jetons={customer.jetons}")

            # Calcul sécurisé de la catégorie
            category = customer.category
            jetons = customer.jetons or 0
            category_name = category.category_name if category else "Unknown"
            current_app.logger.info(f"Category: {category_name}, Jetons: {jetons}")

            # Calcul du pourcentage et des jetons pour le niveau suivant
            percentage = 0
            tokens_to_next_tier = 0
            for i, cat in enumerate(CATEGORIES):
                if cat['min'] <= jetons < cat['max']:
                    range_width = cat['max'] - cat['min']
                    position_in_range = jetons - cat['min']
                    percentage = (position_in_range / range_width) * 100 if range_width > 0 else 0
                    if i + 1 < len(CATEGORIES):
                        tokens_to_next_tier = CATEGORIES[i + 1]['min'] - jetons
                    break
            if not tokens_to_next_tier:
                tokens_to_next_tier = 0
            current_app.logger.info(f"Percentage: {percentage}, Tokens to next tier: {tokens_to_next_tier}")

            # Récupération sécurisée des transactions
            transactions = db.session.query(MyWittiJetonsTransactions).filter_by(
                client_id=customer.id
            ).order_by(MyWittiJetonsTransactions.date_transaction.desc()).limit(5).all()
            
            last_transactions = [
                {
                    "date": t.date_transaction.strftime('%Y-%m-%d') if t.date_transaction else "Unknown",
                    "amount": str(t.montant) if t.montant else "0.00",
                    "type": t.motif or "Unknown"
                }
                for t in transactions
            ]
            current_app.logger.info(f"Transactions fetched: {len(last_transactions)}")

            dashboard = {
                "category": category_name,
                "jetons": jetons,
                "percentage": round(percentage, 2),
                "short_name": customer.short_name or "N/A",
                "tokens_to_next_tier": tokens_to_next_tier,
                "last_transactions": last_transactions
            }

            current_app.logger.info(f"Dashboard retrieved for customer_code: {identifiant}")
            return dashboard, 200

        except Exception as e:
            current_app.logger.error(f"Error fetching dashboard: {str(e)}")
            return {"error": "Internal server error"}, 500

@api.route('/transactions')
class CustomerTransactions(Resource):
    @jwt_required()
    @api.marshal_with(transactions_response_model)
    def get(self):
        try:
            identifiant = get_jwt_identity()
            current_app.logger.info(f"JWT Identity: {identifiant}")

            # Récupération sécurisée du client
            customer = db.session.query(MyWittiClient).filter_by(customer_code=identifiant).first()
            if not customer:
                current_app.logger.warning(f"No customer found for identifiant: {identifiant}")
                return {"message": "Customer not found"}, 404

            # Récupération des paramètres de période et dates personnalisées
            period = request.args.get('period', 'month')
            start_date_str = request.args.get('start_date')
            end_date_str = request.args.get('end_date')

            current_app.logger.info(f"Fetching transactions for period: {period}, start_date: {start_date_str}, end_date: {end_date_str}")

            now = datetime.utcnow()

            # Gestion des dates personnalisées si présentes
            if start_date_str and end_date_str:
                try:
                    period_start = datetime.strptime(start_date_str, '%Y-%m-%d')
                    period_end = datetime.strptime(end_date_str, '%Y-%m-%d')

                    if period_start > period_end:
                        return {"error": "start_date cannot be after end_date"}, 400

                except ValueError as e:
                    current_app.logger.error(f"Invalid date format: {str(e)}")
                    return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400
            else:
                # Calcul des dates selon le period standard
                if period == 'week':
                    period_start = now - timedelta(days=7)
                elif period == 'month':
                    period_start = now - timedelta(days=30)
                elif period == 'year':
                    period_start = now - timedelta(days=365)
                else:
                    period_start = now - timedelta(days=30)  # Par défaut: mois

                period_end = now

            period_start_str = period_start.strftime('%Y-%m-%d')
            period_end_str = period_end.strftime('%Y-%m-%d')

            # Récupération sécurisée des transactions
            transactions = MyWittiJetonsTransactions.query.filter(
                MyWittiJetonsTransactions.client_id == customer.id,
                MyWittiJetonsTransactions.date_transaction >= period_start,
                MyWittiJetonsTransactions.date_transaction <= period_end
            ).order_by(MyWittiJetonsTransactions.date_transaction.desc()).all()

            # Formatage sécurisé des transactions
            transactions_list = []
            for transaction in transactions:
                # Déterminer le type de transaction basé sur le motif
                transaction_type = "Transaction"
                if transaction.motif:
                    motif_upper = transaction.motif.upper()
                    if 'DEPOSIT' in motif_upper or 'DÉPÔT' in motif_upper or 'AJOUT' in motif_upper:
                        transaction_type = "Deposit"
                    elif 'WITHDRAWAL' in motif_upper or 'RETRAIT' in motif_upper or 'SORTIE' in motif_upper:
                        transaction_type = "Withdrawal"
                    elif 'PURCHASE' in motif_upper or 'ACHAT' in motif_upper or 'COMMANDE' in motif_upper:
                        transaction_type = "Purchase"
                    elif 'REWARD' in motif_upper or 'RÉCOMPENSE' in motif_upper or 'BONUS' in motif_upper:
                        transaction_type = "Reward"

                transaction_data = {
                    'date': transaction.date_transaction.strftime('%Y-%m-%d %H:%M:%S') if transaction.date_transaction else "Unknown",
                    'amount': str(transaction.montant) if transaction.montant else "0",
                    'type': transaction_type
                }
                transactions_list.append(transaction_data)

            # Calcul des tendances avec validation
            total_transactions = len(transactions_list)
            deposit_count = sum(1 for t in transactions_list if t['type'] == 'Deposit')
            withdrawal_count = sum(1 for t in transactions_list if t['type'] == 'Withdrawal')

            deposit_percentage = (deposit_count / total_transactions * 100) if total_transactions > 0 else 0
            withdrawal_percentage = (withdrawal_count / total_transactions * 100) if total_transactions > 0 else 0

            trends = {
                "deposit_percentage": round(deposit_percentage, 2),
                "withdrawal_percentage": round(withdrawal_percentage, 2)
            }

            response = {
                "transactions": transactions_list,
                "total_transactions": total_transactions,
                "period_start": period_start_str,
                "period_end": period_end_str,
                "trends": trends
            }

            current_app.logger.info(f"Transactions retrieved for identifiant: {identifiant}, period: {period}, trends: {trends}")
            return response, 200

        except Exception as e:
            current_app.logger.error(f"Error fetching transactions: {str(e)}")
            return {"error": "Internal server error"}, 500

@api.route('/notifications')
class CustomerNotifications(Resource):
    @jwt_required()
    @api.marshal_with(notifications_response_model)
    def get(self):
        try:
            identifiant = get_jwt_identity()
            current_app.logger.info(f"JWT Identity: {identifiant}")

            customer = db.session.query(MyWittiClient).filter_by(customer_code=identifiant).first()
            if not customer:
                current_app.logger.warning(f"No customer found for identifiant: {identifiant}")
                return {"message": "Customer not found"}, 404

            notifications = MyWittiNotification.query.filter_by(
                user_id=customer.user_id
            ).order_by(MyWittiNotification.created_at.desc()).all()

            notifications_data = [{
                'id': notification.id,
                'message': notification.message,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S') if notification.created_at else "Unknown"
            } for notification in notifications]

            return {
                'msg': 'Notifications récupérées avec succès',
                'notifications': notifications_data
            }, 200
        except Exception as e:
            current_app.logger.error(f"Error fetching notifications: {str(e)}")
            return {"error": "Internal server error"}, 500

@api.route('/profile')
class CustomerProfile(Resource):
    @jwt_required()
    @api.marshal_with(profile_model)
    def get(self):
        try:
            identifiant = get_jwt_identity()
            current_app.logger.info(f"JWT Identity: {identifiant}")

            customer = db.session.query(MyWittiClient).filter_by(customer_code=identifiant).first()
            if not customer:
                current_app.logger.warning(f"No customer found for identifiant: {identifiant}")
                return {"message": "Customer not found"}, 404

            # Calcul sécurisé des informations de catégorie et pourcentage
            category = customer.category
            category_name = category.category_name if category else "Unknown"
            
            jetons = customer.jetons or 0
            percentage = 0
            tokens_to_next_tier = 0
            for i, cat in enumerate(CATEGORIES):
                if cat['min'] <= jetons < cat['max']:
                    range_width = cat['max'] - cat['min']
                    position_in_range = jetons - cat['min']
                    percentage = (position_in_range / range_width) * 100 if range_width > 0 else 0
                    if i + 1 < len(CATEGORIES):
                        tokens_to_next_tier = CATEGORIES[i + 1]['min'] - jetons
                    break

            profile = {
                "first_name": customer.first_name or "N/A",
                "short_name": customer.short_name or "N/A",
                "agency": "RGK",
                "jetons": jetons,
                "category": category_name,
                "percentage": round(percentage, 2),
                "tokens_to_next_tier": tokens_to_next_tier
            }

            current_app.logger.info(f"Profile retrieved for identifiant: {identifiant}")
            return profile, 200
        except Exception as e:
            current_app.logger.error(f"Error fetching profile: {str(e)}")
            return {"error": "Internal server error"}, 500

@api.route('/logout')
class CustomerLogout(Resource):
    @jwt_required()
    @api.marshal_with(logout_response_model)
    def post(self):
        try:
            # Récupération sécurisée du JTI du token
            jti = get_jwt()['jti']
            # Ajout du token à la liste noire
            blacklisted_token = TokenBlacklist(jti=jti)
            db.session.add(blacklisted_token)
            db.session.commit()

            current_app.logger.info(f"Customer logged out successfully, token JTI {jti} blacklisted")
            return {"msg": "Déconnexion réussie"}, 200

        except Exception as e:
            current_app.logger.error(f"Error during customer logout: {str(e)}")
            return {"error": "Internal server error"}, 500


# Systeme de parrainage

invite_model = api.model('Invite', {
    'email': fields.String(required=True, description='Email de l\'ami à inviter')
})

# Modèle pour la liste des parrainages
referrals_list_model = api.model('ReferralsList', {
    'referrals': fields.List(fields.Nested(referral_model), description='Liste des parrainages'),
    'total_referrals': fields.Integer(description='Nombre total de parrainages'),
    'pending_count': fields.Integer(description='Nombre de parrainages en attente'),
    'accepted_count': fields.Integer(description='Nombre de parrainages acceptés'),
    'rewarded_count': fields.Integer(description='Nombre de parrainages récompensés')
})

class InviteResource(Resource):
    @jwt_required()
    @api.expect(invite_model)
    def post(self):
        try:
            # Récupération sécurisée de l'utilisateur connecté
            identifiant = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=identifiant).first()
            if not user:
                return {'message': 'Utilisateur non trouvé'}, 404

            # Récupération et validation de l'email de l'ami
            data = request.get_json()
            email = data.get('email')
            if not email:
                return {'message': 'Email requis'}, 400

            # Validation basique de l'email
            if '@' not in email or '.' not in email:
                return {'message': 'Format d\'email invalide'}, 400

            # Vérification si l'email existe déjà dans les parrainages
            existing_referral = MyWittiReferral.query.filter_by(referred_email=email).first()
            if existing_referral:
                return {'message': 'Cet email a déjà été invité'}, 400

            # Création sécurisée d'un nouveau parrainage
            referral_code = str(uuid.uuid4())
            referral = MyWittiReferral(
                referrer_id=user.id,
                referred_email=email,
                referral_code=referral_code,
                status='pending'
            )
            db.session.add(referral)
            db.session.commit()

            referral_link = f"http://127.0.0.1:5000/accounts/refer/{referral_code}"
            return {
                'message': 'Invitation envoyée',
                'referral_link': referral_link
            }, 201

        except Exception as e:
            current_app.logger.error(f"Error creating referral: {str(e)}")
            db.session.rollback()
            return {"error": "Internal server error"}, 500

class MyReferralsResource(Resource):
    @jwt_required()
    @api.marshal_with(referrals_list_model)
    def get(self):
        try:
            # Récupération sécurisée de l'utilisateur connecté
            identifiant = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=identifiant).first()
            if not user:
                return {'message': 'Utilisateur non trouvé'}, 404

            # Récupération sécurisée des parrainages de l'utilisateur
            referrals = MyWittiReferral.query.filter_by(referrer_id=user.id).order_by(MyWittiReferral.created_at.desc()).all()
            
            referrals_data = []
            pending_count = 0
            accepted_count = 0
            rewarded_count = 0
            
            for referral in referrals:
                # Compter les statuts
                if referral.status == 'pending':
                    pending_count += 1
                elif referral.status == 'accepted':
                    accepted_count += 1
                elif referral.status == 'rewarded':
                    rewarded_count += 1
                
                referral_data = {
                    'referral_link': f"http://127.0.0.1:5000/accounts/refer/{referral.referral_code}",
                    'referred_email': referral.referred_email,
                    'status': referral.status,
                    'created_at': referral.created_at.isoformat() if referral.created_at else None
                }
                referrals_data.append(referral_data)

            return {
                'referrals': referrals_data,
                'total_referrals': len(referrals_data),
                'pending_count': pending_count,
                'accepted_count': accepted_count,
                'rewarded_count': rewarded_count
            }, 200

        except Exception as e:
            current_app.logger.error(f"Error fetching referrals: {str(e)}")
            return {"error": "Internal server error"}, 500

api.add_resource(InviteResource, '/invite')
api.add_resource(MyReferralsResource, '/my-referrals')