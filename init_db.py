#!/usr/bin/env python3
"""
Database initialization script for user authentication and profiles.
"""

import os
import sys
from flask import Flask
from models import db, User, AnnotationProfile

def create_app():
    """Create Flask app with database configuration."""
    app = Flask(__name__)
    
    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "ai_annotator.db")}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
    
    # Initialize database
    db.init_app(app)
    
    return app

def init_database():
    """Initialize the database with tables."""
    app = create_app()
    
    with app.app_context():
        print("🗄️ Creating database tables...")
        
        # Create all tables
        db.create_all()
        
        print("✅ Database tables created successfully!")
        print(f"📁 Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Check if any users exist
        user_count = User.query.count()
        profile_count = AnnotationProfile.query.count()
        
        print(f"👤 Users in database: {user_count}")
        print(f"📋 Profiles in database: {profile_count}")
        
        if user_count == 0:
            print("\n💡 Tip: Register your first user by running the application and visiting /register")

def create_admin_user(username, email, password):
    """Create an admin user."""
    app = create_app()
    
    with app.app_context():
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            print(f"❌ User '{username}' already exists!")
            return False
        
        if User.query.filter_by(email=email).first():
            print(f"❌ Email '{email}' is already registered!")
            return False
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        print(f"✅ Admin user '{username}' created successfully!")
        return True

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'create-admin':
        if len(sys.argv) != 5:
            print("Usage: python init_db.py create-admin <username> <email> <password>")
            sys.exit(1)
        
        username, email, password = sys.argv[2], sys.argv[3], sys.argv[4]
        create_admin_user(username, email, password)
    else:
        init_database()