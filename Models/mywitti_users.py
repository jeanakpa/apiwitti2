from extensions import db
from datetime import datetime
from werkzeug.security import check_password_hash
from sqlalchemy import Index, CheckConstraint

class MyWittiUser(db.Model):
    __tablename__ = 'mywitti_users'
    __table_args__ = (
        db.UniqueConstraint('user_id', name='users_user_id_key'),
        Index('idx_mywitti_users_user_type_id', 'user_type_id'),
        Index('idx_users_active', 'user_id', postgresql_where=db.text('is_active = true')),
        Index('idx_users_date_joined', 'date_joined'),
        Index('idx_users_last_login', 'last_login'),
        Index('idx_users_type_active', 'user_type', 'is_active'),
        Index('idx_users_user_type', 'user_type'),
        CheckConstraint("user_type IN ('client', 'admin', 'superadmin')", name='users_user_type_check'),
    )
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    user_type = db.Column(db.String(20), default='client')
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_staff = db.Column(db.Boolean, default=False)
    must_change_password = db.Column(db.Boolean, default=True)
    user_type_id = db.Column(db.Integer, db.ForeignKey('mywitti_user_type.id'))
    email = db.Column(db.String(255))
    user_type_rel = db.relationship('MyWittiUserType', backref='users')
    
    def check_password(self, password):
        """Vérifie si le mot de passe fourni correspond au hash stocké"""
        return check_password_hash(self.password, password)
    
    @property
    def is_admin(self):
        """Retourne True si l'utilisateur est un admin"""
        return self.user_type in ['admin', 'superadmin'] or self.is_staff
    
    @property
    def is_superuser(self):
        """Retourne True si l'utilisateur est un super admin"""
        return self.user_type == 'superadmin' 