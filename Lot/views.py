# Lot/views.py (extrait corrigé)
from flask import Blueprint, current_app, request, jsonify
from flask_restx import Api, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.mywitti_users import MyWittiUser
from Models.mywitti_client import MyWittiClient
from Models.mywitti_lots import MyWittiLot
from Models.mywitti_lots_favoris import MyWittiLotsFavoris
from Models.mywitti_lots_claims import MyWittiLotsClaims
from Models.mywitti_notification import MyWittiNotification
from extensions import db
from datetime import datetime
import uuid

lot_bp = Blueprint('lot', __name__, url_prefix='/lot')
api = Api(lot_bp, version='1.0', title='Lot API', description='API for lot operations')

# Define category ranges
CATEGORIES = [
    {"name": "Eco Premium", "code": "A", "min": 0, "max": 100},
    {"name": "Executive", "code": "B", "min": 100, "max": 1000},
    {"name": "Executive +", "code": "C", "min": 1000, "max": 3000},
    {"name": "First Class", "code": "D", "min": 3000, "max": float('inf')}
]

# Define response models (déjà défini, conservé)
reward_model = api.model('Reward', {
    'id': fields.Integer(description='Reward ID'),
    'title': fields.String(description='Reward title'),
    'tokens_required': fields.Integer(description='Tokens required'),
    'category': fields.String(description='Reward category'),
    'image_url': fields.String(description='Image URL')
})

favorites_response_model = api.model('FavoritesResponse', {
    'count': fields.Integer(description='Number of favorites'),
    'items': fields.List(fields.Nested(reward_model), description='List of favorite rewards')
})

# Modèles de réponse pour l'API
cart_item_model = api.model('CartItem', {
    'id': fields.Integer(description='Item ID'),
    'title': fields.String(description='Item title'),
    'quantity': fields.Integer(description='Quantity'),
    'tokens_required_per_item': fields.Integer(description='Tokens required per item'),
    'total_tokens': fields.Integer(description='Total tokens for this item'),
    'image_url': fields.String(description='Item image URL'),
    'transaction_id': fields.String(description='Transaction ID')
})

order_item_model = api.model('OrderItem', {
    'reward_id': fields.Integer(description='Reward ID'),
    'title': fields.String(description='Item title'),
    'tokens_required_per_item': fields.Integer(description='Tokens required per item'),
    'total_tokens': fields.Integer(description='Total tokens for this item'),
    'image_url': fields.String(description='Item image URL')
})

cart_response_model = api.model('CartResponse', {
    'jetons_disponibles': fields.Integer(description='Available tokens'),
    'jetons_requis': fields.Integer(description='Required tokens'),
    'achat_possible': fields.Boolean(description='Purchase possible'),
    'transactions': fields.List(fields.Nested(cart_item_model), description='Cart items'),
    'notifications': fields.List(fields.String, description='Messages')
})

order_model = api.model('Order', {
    'id': fields.String(description='Order ID'),
    'customer': fields.String(description='Customer name'),
    'contact': fields.String(description='Contact information'),
    'date': fields.String(description='Order date'),
    'heure': fields.String(description='Order time'),
    'amount': fields.Integer(description='Total amount'),
    'items': fields.List(fields.Nested(order_item_model), description='Order items')
})

orders_response_model = api.model('OrdersResponse', {
    'msg': fields.String(description='Success message'),
    'orders': fields.List(fields.Nested(order_model), description='List of orders')
})

@api.route('/rewards')
class AvailableRewards(Resource):
    @jwt_required()
    @api.marshal_list_with(api.model('AvailableReward', {
        'id': fields.Integer,
        'title': fields.String,
        'tokens_required': fields.Integer,
        'image_url': fields.String,
        'category': fields.String,
        'quantity_available': fields.Integer
    }))
    def get(self):
        try:
            # Récupération sécurisée des récompenses avec vérification du stock
            rewards = MyWittiLot.query.filter(MyWittiLot.stock > 0).all()
            available_rewards = []
            
            for reward in rewards:
                # Vérification sécurisée du stock
                quantity_available = reward.stock if reward.stock and reward.stock > 0 else 0
                
                available_rewards.append({
                    "id": reward.id,
                    "title": reward.libelle or "Sans titre",
                    "tokens_required": reward.jetons or 0,
                    "image_url": reward.recompense_image if reward.recompense_image else None,
                    "category": reward.category.category_name if reward.category else "Sans catégorie",
                    "quantity_available": quantity_available
                })
            
            return available_rewards, 200
        except Exception as e:
            current_app.logger.error(f"Error fetching rewards: {str(e)}")
            return {"error": "Internal server error"}, 500

@api.route('/rewards/<int:reward_id>/favorite', methods=['POST'])
class ToggleFavorite(Resource):
    @jwt_required()
    def post(self, reward_id):
        try:
            # Récupération sécurisée de l'utilisateur
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user:
                return {"message": "Utilisateur non trouvé"}, 404

            # Récupération sécurisée du client associé à l'utilisateur
            client = MyWittiClient.query.filter_by(user_id=user.id).first()
            if not client:
                return {"message": "Client non trouvé"}, 404

            # Vérification de l'existence de la récompense
            reward = MyWittiLot.query.get(reward_id)
            if not reward:
                return {"message": "Récompense non trouvée"}, 404

            # Vérification si déjà en favoris
            favorite = MyWittiLotsFavoris.query.filter_by(
                client_id=client.id, 
                lot_id=reward_id
            ).first()
            
            if favorite:
                # Suppression du favori
                db.session.delete(favorite)
                db.session.commit()
                return {"msg": "Récompense retirée des favoris"}
            else:
                # Ajout aux favoris
                new_favorite = MyWittiLotsFavoris(
                    client_id=client.id, 
                    lot_id=reward_id,
                    date_ajout=datetime.utcnow()
                )
                db.session.add(new_favorite)
                db.session.commit()
                return {"msg": "Récompense ajoutée aux favoris"}

        except Exception as e:
            current_app.logger.error(f"Error toggling favorite: {str(e)}")
            db.session.rollback()
            return {"error": "Internal server error"}, 500

@api.route('/favorites', methods=['GET'])
class GetFavorites(Resource):
    @jwt_required()
    @api.marshal_with(favorites_response_model)
    def get(self):
        try:
            # Récupération sécurisée de l'utilisateur
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user:
                return {"message": "Utilisateur non trouvé"}, 404

            # Récupération sécurisée du client associé à l'utilisateur
            client = MyWittiClient.query.filter_by(user_id=user.id).first()
            if not client:
                return {"message": "Client non trouvé"}, 404

            # Récupération sécurisée des favoris
            favorites = MyWittiLotsFavoris.query.filter_by(client_id=client.id).all()
            favorite_rewards = []
            
            for fav in favorites:
                reward = MyWittiLot.query.get(fav.lot_id)
                if reward:
                    favorite_rewards.append({
                        "id": reward.id,
                        "title": reward.libelle or "Sans titre",
                        "tokens_required": reward.jetons or 0,
                        "category": reward.category.category_name if reward.category else "Sans catégorie",
                        "image_url": reward.recompense_image if reward.recompense_image else None
                    })

            return {"count": len(favorite_rewards), "items": favorite_rewards}
        except Exception as e:
            current_app.logger.error(f"Error fetching favorites: {str(e)}")
            return {"error": "Internal server error"}, 500

@api.route('/cart', methods=['POST'])
class AddToCart(Resource):
    @jwt_required()
    def post(self):
        try:
            # Récupération sécurisée de l'utilisateur
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user:
                return {"message": "Utilisateur non trouvé"}, 404

            # Validation des données d'entrée
            data = request.get_json()
            reward_id = data.get('reward_id')
            quantity = data.get('quantity', 1)

            # Validation stricte des entrées
            if not reward_id or quantity <= 0:
                return {"message": "ID de récompense et quantité valides requis"}, 400

            # Vérification de l'existence de la récompense
            reward = MyWittiLot.query.get(reward_id)
            if not reward:
                return {"message": "Récompense non trouvée"}, 404

            # Vérification sécurisée du stock
            if not reward.stock or reward.stock < quantity:
                return {"message": "Quantité insuffisante en stock"}, 400

            # Récupération sécurisée du client associé à l'utilisateur
            customer = MyWittiClient.query.filter_by(user_id=user.id).first()
            if not customer:
                return {"message": "Client non trouvé"}, 404

            # Vérification si l'article est déjà dans le panier
            cart_item = MyWittiLotsClaims.query.filter_by(
                client_id=customer.id, 
                lot_id=reward_id, 
                statut='cart'
            ).first()
            
            if cart_item:
                # Mise à jour de l'article existant (simplifié - dans une vraie app on aurait un champ quantité)
                pass
            else:
                # Création d'un nouvel article dans le panier
                cart_item = MyWittiLotsClaims(
                    client_id=customer.id, 
                    lot_id=reward_id, 
                    statut='cart',
                    date_reclamation=datetime.utcnow()
                )
                db.session.add(cart_item)

            db.session.commit()

            return {
                "msg": f"{reward.libelle} ajoutée au panier",
                "quantity": quantity,
                "total_tokens": quantity * (reward.jetons or 0)
            }
        except Exception as e:
            current_app.logger.error(f"Error adding to cart: {str(e)}")
            db.session.rollback()
            return {"error": "Internal server error"}, 500

@api.route('/cart', methods=['GET'])
class ViewCart(Resource):
    @jwt_required()
    @api.marshal_with(cart_response_model)
    def get(self):
        try:
            # Récupération sécurisée de l'utilisateur
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user:
                return {"message": "Utilisateur non trouvé"}, 404

            # Récupération sécurisée du client associé à l'utilisateur
            customer = MyWittiClient.query.filter_by(user_id=user.id).first()
            if not customer:
                return {"message": "Client non trouvé"}, 404

            # Récupération sécurisée des articles du panier
            cart_items = MyWittiLotsClaims.query.filter_by(
                client_id=customer.id, 
                statut='cart'
            ).all()
            
            transactions = []
            total_required = 0
            
            # Récupération sécurisée du client associé à l'utilisateur
            jetons_disponibles = customer.jetons if customer else 0

            for item in cart_items:
                reward = MyWittiLot.query.get(item.lot_id)
                if reward:
                    transaction = {
                        "id": item.id,
                        "title": reward.libelle or "Sans titre",
                        "quantity": 1,  # Simplifié - supposant 1 par article
                        "tokens_required_per_item": reward.jetons or 0,
                        "total_tokens": reward.jetons or 0,
                        "image_url": reward.recompense_image if reward.recompense_image else None,
                        "transaction_id": str(uuid.uuid4())
                    }
                    transactions.append(transaction)
                    total_required += reward.jetons or 0

            achat_possible = jetons_disponibles >= total_required
            notifications = ["Vérifiez vos jetons disponibles avant l'achat."] if not achat_possible else []

            return {
                "jetons_disponibles": jetons_disponibles,
                "jetons_requis": total_required,
                "achat_possible": achat_possible,
                "transactions": transactions,
                "notifications": notifications
            }
        except Exception as e:
            current_app.logger.error(f"Error viewing cart: {str(e)}")
            return {"error": "Internal server error"}, 500

@api.route('/cart/<int:item_id>', methods=['DELETE'])
class RemoveFromCart(Resource):
    @jwt_required()
    def delete(self, item_id):
        """Supprimer un article du panier"""
        try:
            # Récupération sécurisée de l'utilisateur
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user:
                return {"message": "Utilisateur non trouvé"}, 404

            # Récupération sécurisée du client associé à l'utilisateur
            customer = MyWittiClient.query.filter_by(user_id=user.id).first()
            if not customer:
                return {"message": "Client non trouvé"}, 404

            # Récupération sécurisée de l'article du panier
            cart_item = MyWittiLotsClaims.query.filter_by(
                id=item_id,
                client_id=customer.id,
                statut='cart'
            ).first()
            
            if not cart_item:
                return {"message": "Article non trouvé dans le panier"}, 404

            # Récupération des informations de la récompense pour le message
            reward = MyWittiLot.query.get(cart_item.lot_id)
            reward_name = reward.libelle if reward else "Article"

            # Suppression sécurisée de l'article du panier
            db.session.delete(cart_item)
            db.session.commit()

            return {
                "msg": f"{reward_name} supprimé du panier",
                "item_id": item_id
            }, 200

        except Exception as e:
            current_app.logger.error(f"Error removing from cart: {str(e)}")
            db.session.rollback()
            return {"error": "Internal server error"}, 500

@api.route('/place-order', methods=['POST'])
class PlaceOrder(Resource):
    @jwt_required()
    @api.marshal_with(order_model)
    def post(self):
        try:
            # Récupération sécurisée de l'utilisateur
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user:
                return {"message": "Utilisateur non trouvé"}, 404

            # Récupération sécurisée du client
            customer = MyWittiClient.query.filter_by(user_id=user.id).first()
            if not customer:
                return {"message": "Client non trouvé"}, 404

            # Récupération sécurisée des articles du panier
            cart_items = MyWittiLotsClaims.query.filter_by(
                client_id=customer.id, 
                statut='cart'
            ).all()
            
            if not cart_items:
                return {"message": "Panier vide"}, 400

            total_amount = 0
            items_summary = []

            # Validation et calcul du montant total
            for item in cart_items:
                reward = MyWittiLot.query.get(item.lot_id)
                if not reward:
                    continue

                total_tokens = reward.jetons or 0
                total_amount += total_tokens

                items_summary.append({
                    "reward_id": reward.id,
                    "title": reward.libelle or "Sans titre",
                    "tokens_required_per_item": reward.jetons or 0,
                    "total_tokens": total_tokens,
                    "image_url": reward.recompense_image or ""
                })

                # Mise à jour du statut de l'article à 'pending' (pas de débit immédiat)
                item.statut = 'pending'

            # Vérification sécurisée des jetons disponibles (pour validation future)
            if customer.jetons < total_amount:
                return {"message": "Jetons insuffisants pour cette commande"}, 400

            # IMPORTANT: NE PAS DÉDUIRE LES JETONS ICI - ils seront déduits lors de la validation admin
            # customer.jetons -= total_amount  # ← LIGNE SUPPRIMÉE
            
            db.session.commit()

            # Création sécurisée de la notification pour informer de l'attente
            notification = MyWittiNotification(
                user_id=user.id,
                message=f"Votre commande de {total_amount} jetons a été enregistrée et est en attente de validation par l'administrateur."
            )
            db.session.add(notification)
            db.session.commit()

            return {
                "id": str(uuid.uuid4()),  # Génération d'un ID de commande unique
                "customer": f"{customer.first_name} {customer.short_name}" if customer.first_name and customer.short_name else "N/A",
                "contact": "N/A",
                "date": datetime.utcnow().strftime('%Y-%m-%d'),
                "heure": datetime.utcnow().strftime('%H:%M:%S'),
                "amount": total_amount,
                "items": items_summary
            }
        except Exception as e:
            current_app.logger.error(f"Error placing order: {str(e)}")
            db.session.rollback()
            return {"error": "Internal server error"}, 500