#!/usr/bin/env python3
"""
Script to manage users on your deployed Render application via API calls.
This allows you to grant alpha access to users in your production database.
"""

import requests
import json
import os
from datetime import datetime, timedelta

class RenderUserManager:
    def __init__(self, base_url):
        """Initialize with your Render app URL."""
        self.base_url = base_url.rstrip('/')
        
    def create_admin_api_endpoint(self):
        """
        You'll need to add an admin API endpoint to your Flask app.
        This is a template for the endpoint you should add to app.py
        """
        admin_api_code = '''
# Add this to your app.py file

@app.route('/admin/grant-access', methods=['POST'])
def admin_grant_access():
    """Admin API endpoint to grant premium access."""
    
    # Simple security - you can enhance this
    admin_key = request.headers.get('Admin-Key')
    if admin_key != os.getenv('ADMIN_API_KEY', 'your-secret-admin-key'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    email = data.get('email')
    days = data.get('days', 365)
    access_type = data.get('access_type', 'alpha')
    
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    # Find user
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Grant access
    user.subscription_status = 'active'
    user.subscription_start = datetime.utcnow()
    user.subscription_end = datetime.utcnow() + timedelta(days=days) if days > 0 else None
    user.subscription_id = f"{access_type}_access_{datetime.now().strftime('%Y%m%d')}"
    user.last_payment = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user': user.username,
        'email': user.email,
        'access_type': access_type,
        'expires': user.subscription_end.isoformat() if user.subscription_end else None,
        'profile_limit': user.get_profile_limit()
    })

@app.route('/admin/list-users', methods=['GET'])
def admin_list_users():
    """Admin API endpoint to list users."""
    
    admin_key = request.headers.get('Admin-Key')
    if admin_key != os.getenv('ADMIN_API_KEY', 'your-secret-admin-key'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    users = User.query.all()
    user_list = []
    
    for user in users:
        user_list.append({
            'username': user.username,
            'email': user.email,
            'subscription_status': user.subscription_status,
            'access_type': user.get_access_type(),
            'expires': user.get_access_expires(),
            'profile_count': len(user.annotation_profiles),
            'profile_limit': user.get_profile_limit(),
            'created_at': user.created_at.isoformat()
        })
    
    return jsonify({'users': user_list})
'''
        return admin_api_code
    
    def grant_access_remote(self, email, days=365, access_type='alpha', admin_key='your-secret-admin-key'):
        """Grant access to a user on the remote Render app."""
        
        url = f"{self.base_url}/admin/grant-access"
        headers = {
            'Content-Type': 'application/json',
            'Admin-Key': admin_key
        }
        data = {
            'email': email,
            'days': days,
            'access_type': access_type
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS! Granted {access_type} access to {result['user']}")
                print(f"📧 Email: {result['email']}")
                print(f"🎯 Profile limit: {result['profile_limit']}")
                expires = result['expires']
                print(f"📅 Expires: {expires if expires else 'Never'}")
                return True
            else:
                error = response.json().get('error', 'Unknown error')
                print(f"❌ ERROR: {error}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return False
    
    def list_users_remote(self, admin_key='your-secret-admin-key'):
        """List all users on the remote Render app."""
        
        url = f"{self.base_url}/admin/list-users"
        headers = {'Admin-Key': admin_key}
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                users = result['users']
                
                print("👥 Users on Render Deployment:")
                print("=" * 60)
                
                for user in users:
                    print(f"👤 {user['username']} ({user['email']})")
                    print(f"   Access: {user['access_type']}")
                    print(f"   Status: {user['subscription_status']}")
                    print(f"   Expires: {user['expires']}")
                    print(f"   Profiles: {user['profile_count']}/{user['profile_limit']}")
                    print(f"   Joined: {user['created_at'][:10]}")
                    print("-" * 40)
                
                return users
            else:
                error = response.json().get('error', 'Unknown error')
                print(f"❌ ERROR: {error}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return []

def main():
    """Main function for command line usage."""
    import sys
    
    if len(sys.argv) < 2:
        print("🚀 Render User Manager")
        print("=" * 30)
        print("First, add the admin API endpoints to your app.py:")
        print()
        manager = RenderUserManager("https://example.com")
        print(manager.create_admin_api_endpoint())
        print()
        print("Then use:")
        print("  python3 manage_render_users.py list https://your-app.onrender.com")
        print("  python3 manage_render_users.py grant https://your-app.onrender.com user@email.com")
        print("  python3 manage_render_users.py grant https://your-app.onrender.com user@email.com 30 beta")
        return
    
    command = sys.argv[1].lower()
    
    if len(sys.argv) < 3:
        print("❌ Please provide your Render app URL")
        return
    
    app_url = sys.argv[2]
    manager = RenderUserManager(app_url)
    
    if command == 'list':
        manager.list_users_remote()
        
    elif command == 'grant' and len(sys.argv) >= 4:
        email = sys.argv[3]
        days = int(sys.argv[4]) if len(sys.argv) > 4 else 365
        access_type = sys.argv[5] if len(sys.argv) > 5 else 'alpha'
        manager.grant_access_remote(email, days, access_type)
        
    else:
        print("❌ Invalid command. Use: list or grant")

if __name__ == '__main__':
    main()