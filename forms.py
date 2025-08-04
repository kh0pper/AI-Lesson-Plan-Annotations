#!/usr/bin/env python3
"""
Forms for user authentication and profile management.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User


class RegistrationForm(FlaskForm):
    """User registration form."""
    
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=20, message="Username must be between 3 and 20 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(message="Please enter a valid email address")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters long")
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField('Create Account')
    
    def validate_username(self, username):
        """Check if username is already taken."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email is already registered."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email is already registered. Please use a different email or log in.')


class LoginForm(FlaskForm):
    """User login form."""
    
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class ProfileForm(FlaskForm):
    """Annotation profile creation/editing form."""
    
    name = StringField('Profile Name', validators=[
        DataRequired(),
        Length(min=3, max=50, message="Profile name must be between 3 and 50 characters")
    ])
    description = TextAreaField('Description', validators=[
        Length(max=200, message="Description must be less than 200 characters")
    ])
    set_as_default = BooleanField('Set as Default Profile')
    submit = SubmitField('Save Profile')


class FeedbackForm(FlaskForm):
    """Feedback and bug report form."""
    
    report_type = SelectField('Report Type', choices=[
        ('bug', '🐛 Bug Report'),
        ('feature_request', '💡 Feature Request'),
        ('improvement', '⬆️ Improvement Suggestion'),
        ('other', '💬 Other Feedback')
    ], validators=[DataRequired()])
    
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=5, max=200, message="Title must be between 5 and 200 characters")
    ])
    
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=10, max=2000, message="Description must be between 10 and 2000 characters")
    ], render_kw={
        "placeholder": "Please describe the issue, feature request, or feedback in detail...",
        "rows": 6
    })
    
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical (app is broken)')
    ], default='medium', validators=[DataRequired()])
    
    # Technical details (optional)
    steps_to_reproduce = TextAreaField('Steps to Reproduce (for bugs)', render_kw={
        "placeholder": "1. Go to...\n2. Click on...\n3. See error...",
        "rows": 4
    })
    
    error_details = TextAreaField('Error Details', render_kw={
        "placeholder": "Any error messages, console errors, or technical details...",
        "rows": 3
    })
    
    submit = SubmitField('Submit Feedback')