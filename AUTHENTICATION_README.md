# 🔐 Company Data Scraper - Secure Authentication System

## Overview

The Company Data Scraper now includes a comprehensive authentication system that protects access to the file processing functionality. Users must login with valid credentials before accessing the main application.

## 🚀 Quick Start

### Option 1: Run Batch File (Recommended)
```bash
run_secure_app.bat
```

### Option 2: Run Python Script
```bash
python secure_app_launcher.py
```

## 🔑 Default Login Credentials

**⚠️ IMPORTANT: Change these credentials in production!**

- **Username:** `admin`
- **Password:** `admin123`
- **Role:** `admin`

## 🏗️ Architecture

### Authentication Components

1. **Login GUI** (`gui/login_gui.py`)
   - Secure login interface
   - Session management
   - User-friendly design with status feedback

2. **User Authentication** (`auth/user_auth.py`)
   - Password hashing with salt
   - Session token management
   - Login attempt logging
   - User creation and management

3. **Authenticated Main App** (`gui/authenticated_file_upload_gui.py`)
   - Protected file processing interface
   - Role-based access control
   - Session validation
   - User management (admin only)

4. **Secure Launcher** (`secure_app_launcher.py`)
   - Dependency checking
   - Directory creation
   - Error handling

## 🛡️ Security Features

### Password Security
- **Salted SHA-256 hashing** - Passwords are never stored in plain text
- **Secure session tokens** - Cryptographically secure random tokens
- **Session timeout** - Automatic logout after 1 hour of inactivity

### Access Control
- **Role-based permissions** - Different access levels for users and admins
- **Session validation** - Continuous session checking
- **Login attempt logging** - Track successful and failed login attempts

### Data Protection
- **SQLite database** - Secure local storage for user data
- **IP address logging** - Track login sources
- **Automatic session cleanup** - Remove expired sessions

## 👥 User Management

### User Roles

#### Admin Role
- Full access to all features
- Can create new user accounts
- Can view login attempts and system logs
- Access to system settings

#### User Role
- Access to file upload and processing
- Can view processing status
- Cannot create users or access admin settings

### Creating New Users (Admin Only)

1. Login as admin
2. Navigate to **"👥 User Management"** tab
3. Fill in user details:
   - Username
   - Password
   - Email (optional)
   - Role (user/admin)
4. Click **"Create User"**

## 📊 Features by Tab

### 📁 File Upload Tab
- **File Selection:** Browse and select Excel files
- **Processing Options:** Enable/disable auto-processing
- **Upload Status:** Real-time upload progress
- **LinkedIn Scraping:** Automatic data extraction

### ⚙️ Processing Status Tab
- **Recent Jobs:** View processing history
- **System Status:** Monitor application health
- **Real-time Updates:** Live status information
- **Success Metrics:** Processing statistics

### ⚙️ Settings Tab (Admin Only)
- **Auto-processing Configuration:** System settings
- **Processing Parameters:** LinkedIn scraper settings
- **System Preferences:** Application configuration

### 👥 User Management Tab (Admin Only)
- **Create Users:** Add new user accounts
- **Login Attempts:** Monitor authentication activity
- **Security Logs:** View access attempts
- **User Activity:** Track user sessions

## 🔧 Configuration

### Authentication Settings (`auth/config.ini`)

```ini
[authentication]
session_timeout = 3600          # 1 hour
max_login_attempts = 5
lockout_duration = 30          # 30 minutes

[security]
log_ip_addresses = true
log_sessions = true
force_password_change = false

[application]
enable_user_registration = true
default_user_role = user
```

### Database Location
- **User Database:** `auth/users.db`
- **Login Logs:** `logs/auth.log`

## 🚨 Security Best Practices

### Production Deployment

1. **Change Default Password**
   ```python
   # Create new admin user with secure password
   # Delete default admin account
   ```

2. **Enable HTTPS** (if web-deployed)
   - Use SSL/TLS certificates
   - Secure communication channels

3. **Regular Security Updates**
   - Update dependencies
   - Monitor security logs
   - Review user access

4. **Password Policies**
   - Enforce strong passwords
   - Regular password changes
   - Account lockout policies

### Monitoring

- **Login Attempts:** Check for suspicious activity
- **Session Management:** Monitor active sessions
- **Error Logs:** Review authentication errors
- **Access Patterns:** Analyze user behavior

## 🔄 Session Management

### Session Lifecycle
1. **Login:** Create secure session token
2. **Validation:** Continuous session checking
3. **Extension:** Auto-extend active sessions
4. **Logout:** Secure session termination
5. **Cleanup:** Remove expired sessions

### Session Security
- **Timeout:** 1 hour default (configurable)
- **Token Security:** Cryptographically secure
- **IP Tracking:** Monitor session sources
- **Concurrent Sessions:** Multiple sessions per user

## 🐛 Troubleshooting

### Common Issues

#### "No module named 'PIL'" Error
- **Solution:** The system works without PIL
- **Optional:** Install Pillow for image support: `pip install Pillow`

#### Database Connection Issues
- **Check:** `auth/users.db` file permissions
- **Solution:** Delete database file to recreate

#### Session Expired Errors
- **Cause:** Session timeout reached
- **Solution:** Login again

#### Login Failed
- **Check:** Username/password combination
- **Default:** admin/admin123
- **Solution:** Reset user account if needed

### Debug Mode
```bash
# Enable detailed logging
python secure_app_launcher.py --debug
```

## 📝 Logs and Monitoring

### Log Files
- **Authentication Log:** `logs/auth.log`
- **Application Log:** `logs/app.log`
- **Processing Log:** `logs/processing.log`

### Login Attempts
- View in **User Management** tab (Admin only)
- Includes timestamp, username, IP, and success status
- Helps identify security threats

## 🔄 Updates and Maintenance

### Regular Tasks
1. **Review User Accounts:** Remove inactive users
2. **Check Login Logs:** Monitor suspicious activity
3. **Update Passwords:** Enforce password changes
4. **System Health:** Monitor application performance

### Backup
- **User Database:** Regular backups of `auth/users.db`
- **Configuration:** Backup `auth/config.ini`
- **Logs:** Archive old log files

## 🤝 Support

For support or questions about the authentication system:

1. **Check Logs:** Review error messages in log files
2. **Reset Database:** Delete `auth/users.db` to start fresh
3. **Default Login:** Use admin/admin123 credentials
4. **Configuration:** Modify `auth/config.ini` for custom settings

---

## 🎯 Summary

The authentication system provides enterprise-level security for the Company Data Scraper application:

✅ **Secure Login** - Protected access with encrypted passwords  
✅ **Session Management** - Automatic timeout and token security  
✅ **User Management** - Admin controls for user accounts  
✅ **Role-Based Access** - Different permissions for users and admins  
✅ **Activity Logging** - Complete audit trail of user actions  
✅ **Easy Deployment** - One-click launch with batch file  

**Start the secure application now: `run_secure_app.bat`**