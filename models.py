#!/usr/bin/env python3
"""
Database models for user authentication and annotation profiles.
"""

import json
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication."""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Subscription and billing fields
    stripe_customer_id = db.Column(db.String(100), unique=True)
    subscription_status = db.Column(db.String(20), default='free')  # free, active, past_due, canceled
    subscription_id = db.Column(db.String(100))
    subscription_start = db.Column(db.DateTime)
    subscription_end = db.Column(db.DateTime)
    last_payment = db.Column(db.DateTime)
    
    # Relationships
    annotation_profiles = db.relationship('AnnotationProfile', backref='user', lazy=True, cascade='all, delete-orphan')
    usage_records = db.relationship('UsageRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_premium(self):
        """Check if user has active premium subscription."""
        return self.subscription_status == 'active'
    
    def get_profile_limit(self):
        """Get the maximum number of profiles this user can save."""
        return 10 if self.is_premium() else 1
    
    def get_hourly_usage_limit(self):
        """Get the maximum number of annotations per hour for this user."""
        return 999999 if self.is_premium() else 5  # Effectively unlimited for premium
    
    def get_usage_count_last_hour(self):
        """Get the number of annotations run in the last hour."""
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        return UsageRecord.query.filter(
            UsageRecord.user_id == self.id,
            UsageRecord.created_at >= one_hour_ago
        ).count()
    
    def can_run_annotation(self):
        """Check if user can run another annotation based on rate limits."""
        if self.is_premium():
            return True
        return self.get_usage_count_last_hour() < self.get_hourly_usage_limit()
    
    def can_create_profile(self):
        """Check if user can create another profile."""
        current_count = len(self.annotation_profiles)
        return current_count < self.get_profile_limit()
    
    def __repr__(self):
        return f'<User {self.username}>'


class AnnotationProfile(db.Model):
    """Model for storing user's custom annotation settings."""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Annotation parameters (stored as JSON)
    focus_areas = db.Column(db.JSON)
    pedagogical_approach = db.Column(db.String(50))
    engagement_level = db.Column(db.String(20))
    assessment_type = db.Column(db.String(30))
    differentiation = db.Column(db.String(50))
    language_focus = db.Column(db.String(30))
    age_group = db.Column(db.String(30))
    annotation_theme = db.Column(db.String(30))
    custom_category_definitions = db.Column(db.JSON)
    custom_guidelines = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_default = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert profile to dictionary for form population."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'focus_areas': self.focus_areas or [],
            'pedagogical_approach': self.pedagogical_approach,
            'engagement_level': self.engagement_level,
            'assessment_type': self.assessment_type,
            'differentiation': self.differentiation,
            'language_focus': self.language_focus,
            'age_group': self.age_group,
            'annotation_theme': self.annotation_theme,
            'custom_category_definitions': self.custom_category_definitions or {},
            'custom_guidelines': self.custom_guidelines or '',
            'is_default': self.is_default
        }
    
    @classmethod
    def from_form_data(cls, user_id, name, description, form_data):
        """Create profile from form data."""
        # Extract focus areas
        focus_areas = []
        for key in form_data:
            if key.startswith('focus_area_') and form_data[key]:
                focus_areas.append(form_data[key])
        
        # Extract custom category definitions if using custom theme
        custom_categories = {}
        if form_data.get('annotation_theme') == 'custom':
            for i in range(1, 9):
                definition = form_data.get(f'category{i}_definition', '').strip()
                if definition:
                    custom_categories[f'category{i}'] = definition
        
        return cls(
            user_id=user_id,
            name=name,
            description=description,
            focus_areas=focus_areas,
            pedagogical_approach=form_data.get('pedagogical_approach'),
            engagement_level=form_data.get('engagement_level'),
            assessment_type=form_data.get('assessment_type'),
            differentiation=form_data.get('differentiation'),
            language_focus=form_data.get('language_focus'),
            age_group=form_data.get('age_group'),
            annotation_theme=form_data.get('annotation_theme'),
            custom_category_definitions=custom_categories if custom_categories else None,
            custom_guidelines=form_data.get('custom_guidelines', '').strip()
        )
    
    def __repr__(self):
        return f'<AnnotationProfile {self.name} by {self.user.username}>'


class UsageRecord(db.Model):
    """Model for tracking user annotation usage for rate limiting."""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Optional metadata about the annotation run
    pdf_filename = db.Column(db.String(255))
    tokens_used = db.Column(db.Integer)
    processing_time = db.Column(db.Float)  # seconds
    success = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<UsageRecord user={self.user.username} at {self.created_at}>'