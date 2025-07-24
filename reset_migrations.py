#!/usr/bin/env python3
"""
Script pour réinitialiser complètement les migrations
"""
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

def reset_migrations():
    """Réinitialise complètement les migrations"""
    app = Flask(__name__)
    
    # Configuration directe
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mywitti@localhost:5432/mywitti'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'temp-secret-key-for-reset'
    
    db = SQLAlchemy(app)
    
    with app.app_context():
        try:
            # Supprimer toutes les tables liées à Alembic
            db.session.execute(text("DROP TABLE IF EXISTS alembic_version"))
            db.session.execute(text("DROP TABLE IF EXISTS mywitti_notification"))
            db.session.execute(text("DROP TABLE IF EXISTS mywitti_lots_favoris"))
            db.session.execute(text("DROP TABLE IF EXISTS mywitti_lots_claims"))
            db.session.execute(text("DROP TABLE IF EXISTS mywitti_jetons_transactions"))
            db.session.execute(text("DROP TABLE IF EXISTS mywitti_client_palier_history"))
            db.session.execute(text("DROP TABLE IF EXISTS mywitti_client_jetons_daily"))
            db.session.execute(text("DROP TABLE IF EXISTS mywitti_lots"))
            db.session.execute(text("DROP TABLE IF EXISTS mywitti_client"))
            db.session.execute(text("DROP TABLE IF EXISTS mywitti_comptes"))
            db.session.execute(text("DROP TABLE IF EXISTS mywitti_category"))
            db.session.execute(text("DROP TABLE IF EXISTS mywitti_users"))
            db.session.execute(text("DROP TABLE IF EXISTS mywitti_user_type"))
            db.session.execute(text("DROP TABLE IF EXISTS page_visit"))
            db.session.execute(text("DROP TABLE IF EXISTS mywitti_referral"))
            db.session.execute(text("DROP TABLE IF EXISTS token_blacklist"))
            
            db.session.commit()
            print("✅ Toutes les tables supprimées avec succès")
            
            # Vérifier qu'il ne reste plus de tables
            result = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = [row[0] for row in result.fetchall()]
            
            if not tables:
                print("✅ Base de données complètement vide")
            else:
                print(f"⚠️ Tables restantes : {tables}")
                
        except Exception as e:
            print(f"❌ Erreur lors de la réinitialisation : {e}")
            db.session.rollback()
            return False
            
    return True

if __name__ == "__main__":
    print("🧹 Réinitialisation complète de la base de données...")
    if reset_migrations():
        print("✅ Réinitialisation terminée. Vous pouvez maintenant relancer 'flask db init' et 'flask db migrate'")
    else:
        print("❌ Échec de la réinitialisation")
        sys.exit(1) 