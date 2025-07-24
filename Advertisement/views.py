# Advertisement/views.py
from flask import Blueprint, current_app, request, jsonify
from flask_restx import Api, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.mywitti_users import MyWittiUser
from Models.mywitti_advertisement import MyWittiAdvertisement
from extensions import db
from datetime import datetime
import os
import uuid

advertisement_bp = Blueprint('advertisement', __name__, url_prefix='/advertisement')
api = Api(advertisement_bp, version='1.0', title='Advertisement API', description='API for advertisement management')

# Modèles de réponse pour l'API
advertisement_model = api.model('Advertisement', {
    'id': fields.Integer(description='Advertisement ID'),
    'title': fields.String(description='Advertisement title'),
    'description': fields.String(description='Advertisement description'),
    'image_url': fields.String(description='Image URL'),
    'country': fields.String(description='Target country (null for all countries)'),
    'is_active': fields.Boolean(description='Is advertisement active'),
    'created_at': fields.String(description='Creation date'),
    'updated_at': fields.String(description='Last update date'),
    'created_by': fields.Integer(description='User ID who created the advertisement')
})

advertisement_create_model = api.model('AdvertisementCreate', {
    'title': fields.String(required=True, description='Advertisement title'),
    'description': fields.String(required=True, description='Advertisement description'),
    'image_url': fields.String(required=True, description='Image URL'),
    'country': fields.String(description='Target country (leave empty for all countries)'),
    'is_active': fields.Boolean(description='Is advertisement active', default=True)
})

advertisement_update_model = api.model('AdvertisementUpdate', {
    'title': fields.String(description='Advertisement title'),
    'description': fields.String(description='Advertisement description'),
    'image_url': fields.String(description='Image URL'),
    'country': fields.String(description='Target country (leave empty for all countries)'),
    'is_active': fields.Boolean(description='Is advertisement active')
})

advertisements_response_model = api.model('AdvertisementsResponse', {
    'count': fields.Integer(description='Number of advertisements'),
    'advertisements': fields.List(fields.Nested(advertisement_model), description='List of advertisements')
})

@api.route('/')
class AdvertisementList(Resource):
    @jwt_required()
    @api.marshal_with(advertisements_response_model)
    def get(self):
        """Récupérer toutes les publicités (admin seulement)"""
        try:
            # Vérification des droits admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not user.is_admin:
                return {"message": "Accès refusé. Droits administrateur requis."}, 403

            # Récupération de toutes les publicités
            advertisements = MyWittiAdvertisement.query.order_by(MyWittiAdvertisement.created_at.desc()).all()
            
            advertisements_list = [ad.to_dict() for ad in advertisements]
            
            return {
                "count": len(advertisements_list),
                "advertisements": advertisements_list
            }
        except Exception as e:
            current_app.logger.error(f"Error fetching advertisements: {str(e)}")
            return {"error": "Internal server error"}, 500

    @jwt_required()
    @api.expect(advertisement_create_model)
    @api.marshal_with(advertisement_model)
    def post(self):
        """Créer une nouvelle publicité (admin seulement)"""
        try:
            # Vérification des droits admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not user.is_admin:
                return {"message": "Accès refusé. Droits administrateur requis."}, 403

            # Validation des données d'entrée
            data = request.get_json()
            
            if not data.get('title') or not data.get('description') or not data.get('image_url'):
                return {"message": "Titre, description et image_url sont requis"}, 400

            # Vérification du nombre maximum de publicités actives (3)
            active_count = MyWittiAdvertisement.query.filter_by(is_active=True).count()
            if data.get('is_active', True) and active_count >= 3:
                return {"message": "Maximum 3 publicités actives autorisées"}, 400

            # Création de la nouvelle publicité
            new_advertisement = MyWittiAdvertisement(
                title=data['title'],
                description=data['description'],
                image_url=data['image_url'],
                country=data.get('country'),
                is_active=data.get('is_active', True),
                created_by=user.id
            )
            
            db.session.add(new_advertisement)
            db.session.commit()

            return new_advertisement.to_dict(), 201
        except Exception as e:
            current_app.logger.error(f"Error creating advertisement: {str(e)}")
            db.session.rollback()
            return {"error": "Internal server error"}, 500

@api.route('/<int:advertisement_id>')
class AdvertisementDetail(Resource):
    @jwt_required()
    @api.marshal_with(advertisement_model)
    def get(self, advertisement_id):
        """Récupérer une publicité spécifique (admin seulement)"""
        try:
            # Vérification des droits admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not user.is_admin:
                return {"message": "Accès refusé. Droits administrateur requis."}, 403

            # Récupération de la publicité
            advertisement = MyWittiAdvertisement.query.get(advertisement_id)
            if not advertisement:
                return {"message": "Publicité non trouvée"}, 404

            return advertisement.to_dict()
        except Exception as e:
            current_app.logger.error(f"Error fetching advertisement: {str(e)}")
            return {"error": "Internal server error"}, 500

    @jwt_required()
    @api.expect(advertisement_update_model)
    @api.marshal_with(advertisement_model)
    def put(self, advertisement_id):
        """Modifier une publicité (admin seulement)"""
        try:
            # Vérification des droits admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not user.is_admin:
                return {"message": "Accès refusé. Droits administrateur requis."}, 403

            # Récupération de la publicité
            advertisement = MyWittiAdvertisement.query.get(advertisement_id)
            if not advertisement:
                return {"message": "Publicité non trouvée"}, 404

            # Validation des données d'entrée
            data = request.get_json()
            
            # Vérification du nombre maximum de publicités actives si on active cette publicité
            if data.get('is_active') and not advertisement.is_active:
                active_count = MyWittiAdvertisement.query.filter_by(is_active=True).count()
                if active_count >= 3:
                    return {"message": "Maximum 3 publicités actives autorisées"}, 400

            # Mise à jour des champs
            if 'title' in data:
                advertisement.title = data['title']
            if 'description' in data:
                advertisement.description = data['description']
            if 'image_url' in data:
                advertisement.image_url = data['image_url']
            if 'country' in data:
                advertisement.country = data['country']
            if 'is_active' in data:
                advertisement.is_active = data['is_active']
            
            advertisement.updated_at = datetime.utcnow()
            
            db.session.commit()

            return advertisement.to_dict()
        except Exception as e:
            current_app.logger.error(f"Error updating advertisement: {str(e)}")
            db.session.rollback()
            return {"error": "Internal server error"}, 500

    @jwt_required()
    def delete(self, advertisement_id):
        """Supprimer une publicité (admin seulement)"""
        try:
            # Vérification des droits admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not user.is_admin:
                return {"message": "Accès refusé. Droits administrateur requis."}, 403

            # Récupération de la publicité
            advertisement = MyWittiAdvertisement.query.get(advertisement_id)
            if not advertisement:
                return {"message": "Publicité non trouvée"}, 404

            # Suppression de la publicité
            db.session.delete(advertisement)
            db.session.commit()

            return {"message": "Publicité supprimée avec succès"}, 200
        except Exception as e:
            current_app.logger.error(f"Error deleting advertisement: {str(e)}")
            db.session.rollback()
            return {"error": "Internal server error"}, 500

@api.route('/active')
class ActiveAdvertisements(Resource):
    @api.marshal_list_with(advertisement_model)
    def get(self):
        """Récupérer les publicités actives pour l'application mobile"""
        try:
            # Récupération des publicités actives (maximum 3)
            active_advertisements = MyWittiAdvertisement.query.filter_by(
                is_active=True
            ).order_by(MyWittiAdvertisement.created_at.desc()).limit(3).all()
            
            return [ad.to_dict() for ad in active_advertisements]
        except Exception as e:
            current_app.logger.error(f"Error fetching active advertisements: {str(e)}")
            return {"error": "Internal server error"}, 500

@api.route('/active/<string:country>')
class ActiveAdvertisementsByCountry(Resource):
    @api.marshal_list_with(advertisement_model)
    def get(self, country):
        """Récupérer les publicités actives pour un pays spécifique"""
        try:
            # Récupération des publicités actives pour le pays spécifié ou pour tous les pays
            active_advertisements = MyWittiAdvertisement.query.filter(
                MyWittiAdvertisement.is_active == True,
                db.or_(
                    MyWittiAdvertisement.country == country,
                    MyWittiAdvertisement.country.is_(None)  # Pour les publicités globales
                )
            ).order_by(MyWittiAdvertisement.created_at.desc()).limit(3).all()
            
            return [ad.to_dict() for ad in active_advertisements]
        except Exception as e:
            current_app.logger.error(f"Error fetching active advertisements for country: {str(e)}")
            return {"error": "Internal server error"}, 500

@api.route('/toggle/<int:advertisement_id>')
class ToggleAdvertisement(Resource):
    @jwt_required()
    @api.marshal_with(advertisement_model)
    def post(self, advertisement_id):
        """Activer/Désactiver une publicité (admin seulement)"""
        try:
            # Vérification des droits admin
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not user.is_admin:
                return {"message": "Accès refusé. Droits administrateur requis."}, 403

            # Récupération de la publicité
            advertisement = MyWittiAdvertisement.query.get(advertisement_id)
            if not advertisement:
                return {"message": "Publicité non trouvée"}, 404

            # Vérification si on peut activer (max 3 actives)
            if not advertisement.is_active:
                active_count = MyWittiAdvertisement.query.filter_by(is_active=True).count()
                if active_count >= 3:
                    return {"message": "Maximum 3 publicités actives autorisées"}, 400

            # Basculement du statut
            advertisement.is_active = not advertisement.is_active
            advertisement.updated_at = datetime.utcnow()
            
            db.session.commit()

            return advertisement.to_dict()
        except Exception as e:
            current_app.logger.error(f"Error toggling advertisement: {str(e)}")
            db.session.rollback()
            return {"error": "Internal server error"}, 500 