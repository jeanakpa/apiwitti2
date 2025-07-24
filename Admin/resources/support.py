# admin/resources/support.py
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models.mywitti_users import MyWittiUser
from Models.mywitti_support_request import MyWittiSupportRequest
from Admin.views import api

support_request_model = api.model('SupportRequest', {
    'id': fields.Integer(description='Support Request ID'),
    'user_id': fields.Integer(description='User ID'),
    'subject': fields.String(description='Subject'),
    'description': fields.String(description='Description'),
    'request_type': fields.String(description='Request Type'),
    'created_at': fields.String(description='Created At'),
    'status': fields.String(description='Status')
})

class SupportRequestList(Resource):
    @jwt_required()
    @api.marshal_with(support_request_model, as_list=True)
    def get(self):
        user_id = get_jwt_identity()
        user = MyWittiUser.query.filter_by(user_id=user_id).first()
        if not user or not (user.is_admin or user.is_superuser):
            api.abort(403, "Accès interdit")
        support_requests = MyWittiSupportRequest.query.all()
        return [request.to_dict() for request in support_requests]