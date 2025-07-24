from flask_restx import Resource, fields, Namespace
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.mywitti_users import MyWittiUser
from Models.mywitti_client import MyWittiClient
from Models.mywitti_lots import MyWittiLot
from Models.mywitti_lots_claims import MyWittiLotsClaims
from Models.mywitti_jetons_transactions import MyWittiJetonsTransactions
from Models.page_visit import PageVisit
from extensions import db
from sqlalchemy.sql import desc, func

stats_ns = Namespace('stats', description='Statistics operations')

stats_model = stats_ns.model('Stats', {
    'total_customers': fields.Integer(description='Total Customers'),
    'top_customer_tokens': fields.String(description='Customer with Most Tokens'),
    'pending_orders': fields.Integer(description='Pending Orders'),
    'cancelled_orders': fields.Integer(description='Cancelled Orders'),
    'validated_orders': fields.Integer(description='Validated Orders'),
    'most_visited_pages': fields.String(description='Most Visited Pages'),
    'most_purchased_reward': fields.String(description='Most Purchased Reward')
})

rewards_chart_model = stats_ns.model('RewardsChart', {
    'labels': fields.List(fields.String, description='Noms des récompenses'),
    'data': fields.List(fields.Integer, description="Nombre d'achats par récompense"),
    'colors': fields.List(fields.String, description='Couleurs pour le diagramme')
})

stock_chart_model = stats_ns.model('StockChart', {
    'labels': fields.List(fields.String, description='Noms des articles'),
    'data': fields.List(fields.Integer, description='Stock disponible par article'),
    'colors': fields.List(fields.String, description='Couleurs pour le diagramme')
})

class Stats(Resource):
    @jwt_required()
    @stats_ns.marshal_with(stats_model)
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not (user.is_admin or user.is_superuser):
                stats_ns.abort(403, "Accès interdit - Droits administrateur requis")
            total_customers = MyWittiClient.query.count()
            top_customer = MyWittiClient.query.order_by(MyWittiClient.jetons.desc()).first()
            top_customer_tokens = f"{top_customer.first_name} {top_customer.short_name} ({top_customer.jetons} tokens)" if top_customer and top_customer.first_name and top_customer.short_name else "N/A"
            pending_orders = MyWittiLotsClaims.query.filter_by(statut='pending').count()
            cancelled_orders = MyWittiLotsClaims.query.filter_by(statut='cancelled').count()
            validated_orders = MyWittiLotsClaims.query.filter_by(statut='validated').count()
            most_visited = db.session.query(
                PageVisit.path, 
                func.count(PageVisit.path).label('visit_count')
            ).filter(
                ~PageVisit.path.like('/admin/%')
            ).filter(
                PageVisit.path != '/admin/notifications'
            ).filter(
                PageVisit.path != '/accounts/login'
            ).group_by(PageVisit.path).order_by(
                desc(func.count(PageVisit.path))
            ).limit(3).all()
            most_visited_pages = ", ".join([page[0] for page in most_visited]) if most_visited else "Aucune donnée"
            most_purchased_reward_query = db.session.query(
                MyWittiLot.libelle,
                func.count(MyWittiLotsClaims.lot_id).label('purchase_count')
            ).join(
                MyWittiLotsClaims, 
                MyWittiLot.id == MyWittiLotsClaims.lot_id
            ).filter(
                MyWittiLotsClaims.statut == 'validated'
            ).group_by(
                MyWittiLot.id, 
                MyWittiLot.libelle
            ).order_by(
                desc(func.count(MyWittiLotsClaims.lot_id))
            ).first()
            most_purchased_reward_name = most_purchased_reward_query[0] if most_purchased_reward_query else "N/A"
            return {
                'total_customers': total_customers,
                'top_customer_tokens': top_customer_tokens,
                'pending_orders': pending_orders,
                'cancelled_orders': cancelled_orders,
                'validated_orders': validated_orders,
                'most_visited_pages': most_visited_pages,
                'most_purchased_reward': most_purchased_reward_name
            }
        except Exception as e:
            stats_ns.abort(500, f"Erreur lors du calcul des statistiques: {str(e)}")

class RewardsChart(Resource):
    @jwt_required()
    @stats_ns.marshal_with(rewards_chart_model)
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not (user.is_admin or user.is_superuser):
                stats_ns.abort(403, "Accès interdit - Droits administrateur requis")
            rewards_data = db.session.query(
                MyWittiLot.libelle,
                func.count(MyWittiJetonsTransactions.lot_id).label('purchase_count')
            ).join(
                MyWittiJetonsTransactions,
                MyWittiLot.id == MyWittiJetonsTransactions.lot_id
            ).filter(
                MyWittiJetonsTransactions.lot_id.isnot(None)
            ).group_by(
                MyWittiLot.id,
                MyWittiLot.libelle
            ).order_by(
                desc(func.count(MyWittiJetonsTransactions.lot_id))
            ).limit(10).all()
            labels = []
            data = []
            colors = [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
            ]
            for i, (libelle, count) in enumerate(rewards_data):
                labels.append(libelle or "Sans nom")
                data.append(count)
            return {
                'labels': labels,
                'data': data,
                'colors': colors[:len(labels)]
            }
        except Exception as e:
            stats_ns.abort(500, f"Erreur lors de la récupération des données de récompenses: {str(e)}")

class StockChart(Resource):
    @jwt_required()
    @stats_ns.marshal_with(stock_chart_model)
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = MyWittiUser.query.filter_by(user_id=user_id).first()
            if not user or not (user.is_admin or user.is_superuser):
                stats_ns.abort(403, "Accès interdit - Droits administrateur requis")
            stock_data = db.session.query(
                MyWittiLot.libelle,
                MyWittiLot.stock
            ).filter(
                MyWittiLot.stock > 0
            ).order_by(
                MyWittiLot.stock.desc()
            ).limit(10).all()
            labels = []
            data = []
            colors = [
                '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                '#FF9F40', '#FF6384', '#C9CBCF', '#4BC0C0', '#FF6384'
            ]
            for i, (libelle, stock) in enumerate(stock_data):
                labels.append(libelle or "Sans nom")
                data.append(stock or 0)
            return {
                'labels': labels,
                'data': data,
                'colors': colors[:len(labels)]
            }
        except Exception as e:
            stats_ns.abort(500, f"Erreur lors de la récupération des données de stock: {str(e)}")

# Export for use in Admin/views.py
__all__ = ['Stats', 'RewardsChart', 'StockChart', 'stats_ns', 'stats_model', 'rewards_chart_model', 'stock_chart_model']