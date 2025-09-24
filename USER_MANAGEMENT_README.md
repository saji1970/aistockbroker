# AI Stock Trading Platform - User Management System

## Overview

This document describes the comprehensive user management system implemented for the AI Stock Trading Platform. The system provides secure authentication, role-based access control, user profiles, and admin functionality.

## Features

### 🔐 Authentication
- **User Registration**: Email and username-based registration with strong password validation
- **Login/Logout**: Secure authentication with JWT tokens and session management
- **Password Reset**: Email-based password reset functionality
- **Session Management**: Automatic token refresh and session expiration handling
- **Multi-Session Support**: Users can have multiple active sessions with individual logout capability

### 👥 User Profiles
- **Basic Information**: Name, email, username management
- **Trading Preferences**: Experience level, risk tolerance, investment goals
- **Profile Customization**: Preferred sectors, initial capital settings
- **Account Status Tracking**: Active, pending, suspended, inactive states

### 🛡️ Role-Based Access Control (RBAC)
- **Admin Role**: Full system access, user management capabilities
- **User Role**: Standard user access to trading features
- **Guest Role**: Limited access for trial users
- **Permission System**: Fine-grained access control for different features

### 👨‍💼 Admin Dashboard
- **User Management**: View, edit, suspend, activate, and delete users
- **Dashboard Statistics**: User counts, status breakdowns, activity metrics
- **Bulk Operations**: Mass status updates and user management
- **Audit Logging**: Complete activity tracking for security and compliance

### 🔍 Security Features
- **Password Security**: Bcrypt hashing with salt
- **Input Validation**: Comprehensive data validation and sanitization
- **Rate Limiting**: Protection against brute force attacks
- **CSRF Protection**: Cross-site request forgery protection
- **Session Security**: HTTP-only cookies, secure tokens
- **Audit Trail**: Complete logging of user actions and admin operations

## Architecture

### Backend Components

```
backend/
├── models/
│   ├── __init__.py
│   └── user.py              # Database models
├── services/
│   ├── __init__.py
│   ├── auth_service.py      # Authentication logic
│   └── user_service.py      # User management operations
├── middleware/
│   ├── __init__.py
│   └── auth_middleware.py   # Authentication middleware
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py       # Authentication endpoints
│   └── user_routes.py       # User management endpoints
├── database.py              # Database configuration
├── setup_user_system.py     # Setup script
└── test_user_system.py      # Test script
```

### Frontend Components

```
frontend/src/
├── services/
│   ├── authService.js       # Authentication service
│   └── adminService.js      # Admin operations service
├── contexts/
│   └── AuthContext.js       # Authentication context
├── components/
│   ├── Auth/
│   │   ├── LoginForm.js     # Login form component
│   │   ├── RegisterForm.js  # Registration form component
│   │   ├── ProfilePage.js   # User profile management
│   │   └── ProtectedRoute.js # Route protection component
│   └── Admin/
│       ├── AdminDashboard.js    # Admin dashboard
│       └── UserManagement.js    # User management interface
```

## Database Schema

### Users Table
- `id`: Primary key
- `email`: Unique user email
- `username`: Unique username
- `password_hash`: Bcrypt hashed password
- `first_name`, `last_name`: User's name
- `role`: User role (admin, user, guest)
- `status`: Account status (active, pending, suspended, inactive)
- `trading_experience`: Beginner, intermediate, advanced
- `risk_tolerance`: Low, medium, high
- `investment_goals`: Text field for goals
- `preferred_sectors`: JSON string of preferred sectors
- `initial_capital`: Starting capital amount
- Timestamps: `created_at`, `updated_at`, `last_login`, `email_verified_at`
- OAuth: `google_id`, `github_id` (for future OAuth integration)

### User Sessions Table
- Session token management
- IP address and user agent tracking
- Expiration and refresh token handling
- Remember me functionality

### Password Resets Table
- Secure password reset token management
- Expiration and usage tracking

### Audit Logs Table
- Complete action logging
- User and admin action tracking
- Request context and metadata
- Security event monitoring

## API Endpoints

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/verify-session` - Verify session validity
- `POST /api/auth/forgot-password` - Request password reset
- `POST /api/auth/reset-password` - Reset password with token
- `POST /api/auth/refresh-token` - Refresh authentication token

### User Management Endpoints
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `POST /api/users/change-password` - Change password

### Admin Endpoints
- `GET /api/users` - List users (with pagination and filters)
- `GET /api/users/:id` - Get user by ID
- `PUT /api/users/:id` - Update user
- `PUT /api/users/:id/role` - Update user role
- `PUT /api/users/:id/status` - Update user status
- `DELETE /api/users/:id` - Delete user
- `GET /api/users/:id/audit-logs` - Get user audit logs
- `GET /api/users/dashboard/stats` - Get dashboard statistics

## Setup Instructions

### 1. Backend Setup

#### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Environment Variables
Create a `.env` file in the backend directory:
```env
# Database
DATABASE_URL=sqlite:///trading_platform.db  # or PostgreSQL URL

# JWT Authentication
JWT_SECRET_KEY=your-super-secret-jwt-key-here

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

# Admin User (for initial setup)
ADMIN_EMAIL=admin@aitrading.com
ADMIN_USERNAME=admin
ADMIN_PASSWORD=AdminPassword123!
ADMIN_FIRST_NAME=System
ADMIN_LAST_NAME=Administrator

# Development
FLASK_ENV=development
CREATE_TEST_USERS=true
```

#### Initialize Database
```bash
cd backend
python setup_user_system.py setup
```

#### Run Backend Server
```bash
cd backend
python api_server.py
```

### 2. Frontend Setup

#### Install Dependencies
```bash
cd frontend
npm install
```

#### Update Configuration
Ensure `frontend/src/services/config.js` points to your backend:
```javascript
export const config = {
  apiBaseUrl: 'http://localhost:8080/api'
};
```

#### Run Frontend Development Server
```bash
cd frontend
npm start
```

### 3. Integration with Existing App

#### Update App.js
```jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute, AdminRoute, GuestRoute } from './components/Auth/ProtectedRoute';
import LoginForm from './components/Auth/LoginForm';
import RegisterForm from './components/Auth/RegisterForm';
import ProfilePage from './components/Auth/ProfilePage';
import AdminDashboard from './components/Admin/AdminDashboard';
import UserManagement from './components/Admin/UserManagement';
// Your existing components
import Dashboard from './pages/Dashboard';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Guest routes (accessible only when not logged in) */}
            <Route
              path="/login"
              element={
                <GuestRoute>
                  <LoginForm />
                </GuestRoute>
              }
            />
            <Route
              path="/register"
              element={
                <GuestRoute>
                  <RegisterForm />
                </GuestRoute>
              }
            />

            {/* Protected user routes */}
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute requireTrading={true}>
                  <Dashboard />
                </ProtectedRoute>
              }
            />

            {/* Admin routes */}
            <Route
              path="/admin"
              element={
                <AdminRoute>
                  <AdminDashboard />
                </AdminRoute>
              }
            />
            <Route
              path="/admin/users"
              element={
                <AdminRoute>
                  <UserManagement />
                </AdminRoute>
              }
            />

            {/* Your existing routes */}
            {/* ... */}
          </Routes>

          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
```

## Testing

### Backend Tests
```bash
cd backend
python test_user_system.py
```

### Manual Testing Checklist
- [ ] User registration with valid data
- [ ] User registration with invalid data (email format, weak password)
- [ ] User login with valid credentials
- [ ] User login with invalid credentials
- [ ] Password reset flow
- [ ] Profile updates
- [ ] Session management (token refresh)
- [ ] Admin user creation
- [ ] Admin dashboard access
- [ ] User management operations (role/status updates)
- [ ] Bulk operations
- [ ] Audit log generation

## Security Considerations

### Implemented Security Measures
1. **Password Security**: Bcrypt hashing with unique salts
2. **JWT Security**: Secure token generation and validation
3. **Input Validation**: Comprehensive validation on all inputs
4. **Rate Limiting**: Protection against brute force attacks
5. **SQL Injection Prevention**: Parameterized queries via SQLAlchemy
6. **XSS Prevention**: Input sanitization and output encoding
7. **CSRF Protection**: Anti-CSRF tokens for state-changing operations
8. **Session Security**: HTTP-only cookies, secure transmission
9. **Audit Logging**: Complete action tracking for security monitoring

### Additional Recommendations
1. **HTTPS**: Always use HTTPS in production
2. **Database Security**: Use strong database credentials and network isolation
3. **Environment Variables**: Store sensitive configuration in environment variables
4. **Regular Updates**: Keep dependencies updated for security patches
5. **Monitoring**: Implement security monitoring and alerting
6. **Backup**: Regular database backups with encryption

## Deployment

### Environment-Specific Configuration

#### Development
- SQLite database
- Debug mode enabled
- Test user creation
- Relaxed security settings

#### Production
- PostgreSQL database
- Debug mode disabled
- Strong JWT secrets
- Email verification enabled
- HTTPS enforcement
- Enhanced rate limiting

### Docker Deployment
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python setup_user_system.py setup

EXPOSE 8080
CMD ["python", "api_server.py"]
```

### Environment Variables for Production
```env
DATABASE_URL=postgresql://user:password@db:5432/trading_platform
JWT_SECRET_KEY=your-production-jwt-secret
FLASK_ENV=production
SMTP_SERVER=your-smtp-server
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password
ADMIN_EMAIL=admin@yourcompany.com
ADMIN_PASSWORD=your-secure-admin-password
```

## Troubleshooting

### Common Issues

#### "Database not initialized" Error
```bash
cd backend
python setup_user_system.py setup
```

#### "JWT_SECRET_KEY not found" Warning
Set the JWT_SECRET_KEY environment variable:
```bash
export JWT_SECRET_KEY=your-secret-key
```

#### "Permission denied" on User Operations
Verify the user has the correct role and active status.

#### Frontend Can't Connect to Backend
Check that:
1. Backend server is running on the correct port
2. CORS origins include your frontend URL
3. API base URL in config.js is correct

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

### Planned Features
1. **OAuth Integration**: Google and GitHub OAuth login
2. **Email Verification**: Complete email verification flow
3. **Two-Factor Authentication**: TOTP-based 2FA
4. **Advanced RBAC**: Custom permissions and role hierarchies
5. **User Groups**: Organize users into trading groups
6. **API Rate Limiting**: Per-user API rate limiting
7. **Advanced Audit**: Enhanced audit trails with search and filtering
8. **Mobile App Support**: React Native integration
9. **Notification System**: Email and in-app notifications
10. **Advanced Security**: IP whitelisting, device tracking

### API Versioning
Future API versions will maintain backward compatibility:
- `/api/v1/auth/*` - Current version
- `/api/v2/auth/*` - Future version with enhanced features

## Support

For issues and questions:
1. Check this documentation
2. Review the troubleshooting section
3. Check server logs for error details
4. Verify environment configuration
5. Test with the provided test script

## License

This user management system is part of the AI Stock Trading Platform and follows the same licensing terms as the main project.