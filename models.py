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
    feedback_reports = db.relationship('FeedbackReport', backref='user', lazy=True, cascade='all, delete-orphan')
    
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
    
    def is_alpha_tester(self):
        """Check if user is an alpha tester."""
        return (self.subscription_id and 
                ('alpha_access' in self.subscription_id or 'beta_access' in self.subscription_id))
    
    def get_access_type(self):
        """Get the user's access type for display."""
        if not self.is_premium():
            return "Free"
        elif self.subscription_id:
            if 'alpha_access' in self.subscription_id:
                return "Alpha Tester"
            elif 'beta_access' in self.subscription_id:
                return "Beta Tester"
            elif self.subscription_id.startswith('sub_'):
                return "Premium Subscriber"
            else:
                return "Premium Access"
        return "Premium"
    
    def get_access_expires(self):
        """Get when access expires, formatted for display."""
        if not self.subscription_end:
            return "Never"
        return self.subscription_end.strftime('%B %d, %Y')
    
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


class FeedbackReport(db.Model):
    """Model for storing user feedback, bug reports, and feature requests."""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Report details
    report_type = db.Column(db.String(20), nullable=False)  # bug, feature_request, improvement, other
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(10), default='medium')  # low, medium, high, critical
    
    # Admin fields
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    admin_notes = db.Column(db.Text)
    assigned_to = db.Column(db.String(100))  # admin email or name
    resolved_at = db.Column(db.DateTime)
    
    # Optional technical details
    browser_info = db.Column(db.String(500))
    error_details = db.Column(db.Text)
    steps_to_reproduce = db.Column(db.Text)
    
    def to_dict(self):
        """Convert feedback report to dictionary."""
        return {
            'id': self.id,
            'user': {
                'username': self.user.username,
                'email': self.user.email,
                'access_type': self.user.get_access_type()
            },
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'report_type': self.report_type,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'admin_notes': self.admin_notes,
            'assigned_to': self.assigned_to,
            'resolved_at': self.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if self.resolved_at else None,
            'browser_info': self.browser_info,
            'error_details': self.error_details,
            'steps_to_reproduce': self.steps_to_reproduce
        }
    
    def get_status_badge(self):
        """Get HTML badge for status."""
        badges = {
            'open': '<span class="badge bg-primary">Open</span>',
            'in_progress': '<span class="badge bg-warning text-dark">In Progress</span>',
            'resolved': '<span class="badge bg-success">Resolved</span>',
            'closed': '<span class="badge bg-secondary">Closed</span>'
        }
        return badges.get(self.status, f'<span class="badge bg-light text-dark">{self.status}</span>')
    
    def get_priority_badge(self):
        """Get HTML badge for priority."""
        badges = {
            'low': '<span class="badge bg-light text-dark">Low</span>',
            'medium': '<span class="badge bg-info">Medium</span>',
            'high': '<span class="badge bg-warning text-dark">High</span>',
            'critical': '<span class="badge bg-danger">Critical</span>'
        }
        return badges.get(self.priority, f'<span class="badge bg-light text-dark">{self.priority}</span>')
    
    def get_type_badge(self):
        """Get HTML badge for report type."""
        badges = {
            'bug': '<span class="badge bg-danger"><i class="fas fa-bug me-1"></i>Bug</span>',
            'feature_request': '<span class="badge bg-success"><i class="fas fa-lightbulb me-1"></i>Feature</span>',
            'improvement': '<span class="badge bg-primary"><i class="fas fa-arrow-up me-1"></i>Improvement</span>',
            'other': '<span class="badge bg-secondary"><i class="fas fa-comment me-1"></i>Other</span>'
        }
        return badges.get(self.report_type, f'<span class="badge bg-light text-dark">{self.report_type}</span>')
    
    def __repr__(self):
        return f'<FeedbackReport {self.report_type}: {self.title} by {self.user.username}>'


class GiftCard(db.Model):
    """Model for storing gift card codes and redemption tracking."""
    
    __tablename__ = 'gift_cards'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    value_months = db.Column(db.Integer, nullable=False, default=1)  # Premium months
    is_redeemed = db.Column(db.Boolean, nullable=False, default=False)
    
    # Purchase tracking
    purchase_source = db.Column(db.String(50), nullable=False, default='Teachers Pay Teachers')
    purchase_id = db.Column(db.String(100))  # External purchase/order ID
    purchase_email = db.Column(db.String(255))  # Purchaser's email
    purchase_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Redemption tracking
    redeemed_by_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    redeemed_at = db.Column(db.DateTime, nullable=True)
    redeemed_ip = db.Column(db.String(45))  # IP address of redemption
    
    # Expiration (optional - gift cards could expire)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Metadata
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)  # Admin notes
    
    # Relationships
    redeemed_by = db.relationship('User', backref=db.backref('redeemed_gift_cards', lazy='dynamic'))
    
    def is_valid(self):
        """Check if gift card is valid for redemption."""
        if self.is_redeemed:
            return False, "Gift card has already been redeemed"
        
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False, "Gift card has expired"
        
        return True, "Gift card is valid"
    
    def redeem(self, user, client_ip=None):
        """Redeem the gift card for a user."""
        is_valid, message = self.is_valid()
        if not is_valid:
            print(f"❌ Gift card validation failed: {message}")
            return False, message
        
        try:
            print(f"🎁 Starting redemption for gift card {self.code} by user {user.username}")
            
            # Mark as redeemed
            self.is_redeemed = True
            self.redeemed_by_user_id = user.id
            self.redeemed_at = datetime.utcnow()
            self.redeemed_ip = client_ip
            
            # Grant premium access
            from datetime import timedelta
            
            print(f"📊 User before redemption: access_type={user.access_type}, expires_at={user.expires_at}")
            
            # If user already has premium access, extend it
            if user.expires_at and user.expires_at > datetime.utcnow():
                user.expires_at = user.expires_at + timedelta(days=30 * self.value_months)
            else:
                user.expires_at = datetime.utcnow() + timedelta(days=30 * self.value_months)
            
            # Update user access type
            if user.access_type == 'Free':
                user.access_type = 'Premium Access'
            
            user.subscription_status = 'active'
            user.profile_limit = 10
            
            print(f"📊 User after update: access_type={user.access_type}, expires_at={user.expires_at}")
            print(f"💾 Attempting database commit...")
            
            db.session.commit()
            
            print(f"✅ Gift card {self.code} redeemed successfully!")
            return True, f"Gift card redeemed! Premium access granted until {user.expires_at.strftime('%B %d, %Y')}"
            
        except Exception as e:
            print(f"❌ Error during gift card redemption: {str(e)}")
            print(f"❌ Exception type: {type(e).__name__}")
            db.session.rollback()
            return False, f"Database error during redemption: {str(e)}"
    
    def to_dict(self):
        """Convert gift card to dictionary for API responses."""
        return {
            'id': self.id,
            'code': self.code,
            'value_months': self.value_months,
            'is_redeemed': self.is_redeemed,
            'purchase_source': self.purchase_source,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'redeemed_at': self.redeemed_at.isoformat() if self.redeemed_at else None,
            'redeemed_by': self.redeemed_by.username if self.redeemed_by else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat()
        }
    
    @staticmethod
    def generate_code():
        """Generate a unique gift card code."""
        import secrets
        import string
        
        # Generate a secure random code (format: XXXX-XXXX-XXXX)
        chars = string.ascii_uppercase + string.digits
        while True:
            code = '-'.join([''.join(secrets.choice(chars) for _ in range(4)) for _ in range(3)])
            
            # Ensure code is unique
            if not GiftCard.query.filter_by(code=code).first():
                return code
    
    def get_status_badge(self):
        """Get HTML badge for redemption status."""
        if self.is_redeemed:
            return '<span class="badge bg-success"><i class="fas fa-check me-1"></i>Redeemed</span>'
        elif self.expires_at and self.expires_at < datetime.utcnow():
            return '<span class="badge bg-danger"><i class="fas fa-times me-1"></i>Expired</span>'
        else:
            return '<span class="badge bg-primary"><i class="fas fa-gift me-1"></i>Active</span>'
    
    def __repr__(self):
        return f'<GiftCard {self.code}: {self.value_months} months, {"Redeemed" if self.is_redeemed else "Active"}>'