# Admin Panel Security Configuration

The admin panel has been secured with multiple layers of authentication and authorization.

## Security Layers

### 1. User Authentication
- Must be logged in with a valid user account
- Uses Flask-Login session management

### 2. Admin Email Whitelist
- Only users with emails in `ADMIN_EMAILS` environment variable can access admin functions
- Format: `ADMIN_EMAILS=admin1@domain.com,admin2@domain.com`

### 3. Admin Password (Optional)
- Additional password protection with `ADMIN_PASSWORD` environment variable
- If set, requires separate admin password entry
- Admin sessions are tracked separately from user sessions

### 4. API Key Protection
- Admin API endpoints require `Admin-Key` header
- Set via `ADMIN_API_KEY` environment variable (default: `ai-lesson-alpha-admin-2024`)

### 5. IP Whitelist (Optional)
- Restrict admin API access to specific IP addresses
- Set via `ADMIN_IP_WHITELIST` environment variable
- Format: `ADMIN_IP_WHITELIST=192.168.1.100,10.0.0.5`

## Environment Variables

### Required for Admin Access
```bash
# Admin user email addresses (comma-separated)
ADMIN_EMAILS=your-email@domain.com,admin2@domain.com

# Admin API key for API endpoints
ADMIN_API_KEY=your-secure-admin-key-here
```

### Optional Security Enhancements
```bash
# Additional admin password protection
ADMIN_PASSWORD=your-secure-admin-password

# IP whitelist for API access (comma-separated)
ADMIN_IP_WHITELIST=your.ip.address.here,second.ip.here
```

## Setup Instructions

### 1. Configure Admin Users
Add your email to Render environment variables:
```
ADMIN_EMAILS=your-email@domain.com
```

### 2. Change Default API Key
```
ADMIN_API_KEY=your-unique-secure-key-2024
```

### 3. Optional: Add Admin Password
```
ADMIN_PASSWORD=YourSecureAdminPassword123!
```

### 4. Optional: Restrict by IP
```
ADMIN_IP_WHITELIST=your.home.ip.address
```

## Access Flow

1. **Login** to your user account first
2. **Navigate** to `/admin` 
3. **Verify** you're in the admin email list
4. **Enter** admin password (if configured)
5. **Access** granted to admin panel

## Security Features

### ✅ Multi-Layer Authentication
- User login + admin whitelist + optional password
- Session-based admin verification
- API key protection for endpoints

### ✅ Access Logging
- All admin actions are logged with timestamps
- Includes admin user email and IP address
- Tracks grant/revoke operations

### ✅ Secure Session Management
- Admin sessions are separate from user sessions
- Admin logout clears admin privileges only
- Sessions timeout with user logout

### ✅ IP-Based Restrictions
- Optional IP whitelist for API endpoints
- Protects against remote API abuse
- Logs client IP addresses

## Admin URLs

- **Admin Panel**: `/admin` (requires full authentication)
- **Admin Login**: `/admin/login` (password verification)
- **Admin Logout**: `/admin/logout` (clears admin session)

## API Endpoints

All require `Admin-Key` header + authentication:

- `POST /admin/grant-access` - Grant premium access
- `GET /admin/list-users` - List all users  
- `POST /admin/revoke-access` - Revoke premium access

## Security Best Practices

1. **Use strong, unique admin passwords**
2. **Limit admin emails to trusted addresses only**
3. **Change default API keys**
4. **Enable IP whitelist for production**
5. **Monitor admin action logs regularly**
6. **Use HTTPS in production (Render provides this)**

## Emergency Access Revocation

To immediately revoke admin access:

1. Remove email from `ADMIN_EMAILS` environment variable
2. Change `ADMIN_API_KEY` environment variable
3. Admin sessions will be invalidated on next request

## Troubleshooting

### "Access denied. Admin privileges required."
- Check that your email is in `ADMIN_EMAILS` environment variable
- Ensure you're logged into the correct user account

### "Invalid admin password"
- Check `ADMIN_PASSWORD` environment variable
- Password is case-sensitive

### "Unauthorized access" on API endpoints
- Verify `Admin-Key` header matches `ADMIN_API_KEY`
- Check IP whitelist if configured
- Ensure proper authentication

## Security Audit Log

All admin actions are logged in this format:
```
🔐 ADMIN ACTION: admin@domain.com (IP: 192.168.1.100) granted alpha access to user@domain.com
```

Monitor your application logs for these entries to track admin activity.