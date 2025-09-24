#!/usr/bin/env python3
"""
Setup script for user management system
Creates database tables and initial admin user
"""

import os
import sys
from datetime import datetime, timezone
import logging

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager, init_database
from models import User, UserRole, UserStatus
from services.auth_service import auth_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin_user(email, username, password, first_name=None, last_name=None):
    """Create an admin user"""
    with db_manager.get_session() as session:
        try:
            # Check if admin user already exists
            existing_user = session.query(User).filter(
                (User.email == email.lower()) | (User.username == username)
            ).first()

            if existing_user:
                logger.info(f"Admin user already exists: {existing_user.email}")
                return {
                    'id': existing_user.id,
                    'email': existing_user.email,
                    'username': existing_user.username,
                    'role': existing_user.role.value if existing_user.role else None
                }

            # Create admin user
            admin_user = User(
                email=email,
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=UserRole.ADMIN,
                status=UserStatus.ACTIVE,
                email_verified_at=datetime.now(timezone.utc)
            )

            session.add(admin_user)
            session.flush()

            logger.info(f"Admin user created: {admin_user.email}")
            # Return a dict instead of the model instance to avoid session issues
            return {
                'id': admin_user.id,
                'email': admin_user.email,
                'username': admin_user.username,
                'role': admin_user.role.value if admin_user.role else None
            }

        except Exception as e:
            logger.error(f"Error creating admin user: {e}")
            raise

def create_test_users():
    """Create some test users for development"""
    test_users = [
        {
            'email': 'user1@example.com',
            'username': 'testuser1',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': UserRole.USER,
            'status': UserStatus.ACTIVE
        },
        {
            'email': 'user2@example.com',
            'username': 'testuser2',
            'password': 'TestPassword123!',
            'first_name': 'Demo',
            'last_name': 'User',
            'role': UserRole.USER,
            'status': UserStatus.PENDING
        }
    ]

    with db_manager.get_session() as session:
        created_users = []

        for user_data in test_users:
            try:
                # Check if user already exists
                existing_user = session.query(User).filter(
                    (User.email == user_data['email'].lower()) |
                    (User.username == user_data['username'])
                ).first()

                if existing_user:
                    logger.info(f"Test user already exists: {existing_user.email}")
                    continue

                # Create test user
                user = User(
                    email=user_data['email'],
                    username=user_data['username'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    status=user_data['status'],
                    email_verified_at=datetime.now(timezone.utc) if user_data['status'] == UserStatus.ACTIVE else None
                )

                session.add(user)
                created_users.append(user)

                logger.info(f"Test user created: {user.email}")

            except Exception as e:
                logger.error(f"Error creating test user {user_data['email']}: {e}")

        return created_users

def setup_user_system():
    """Setup the complete user management system"""
    try:
        logger.info("Setting up user management system...")

        # Initialize database
        logger.info("Initializing database...")
        init_database()

        # Check database connectivity
        if not db_manager.health_check():
            raise Exception("Database health check failed")

        logger.info("Database initialized successfully")

        # Create admin user
        logger.info("Creating admin user...")
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@aitrading.com')
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'AdminPassword123!')
        admin_first_name = os.environ.get('ADMIN_FIRST_NAME', 'System')
        admin_last_name = os.environ.get('ADMIN_LAST_NAME', 'Administrator')

        admin_user = create_admin_user(
            email=admin_email,
            username=admin_username,
            password=admin_password,
            first_name=admin_first_name,
            last_name=admin_last_name
        )

        logger.info(f"Admin user ready: {admin_user['email']}")

        # Create test users in development
        if os.environ.get('FLASK_ENV') == 'development' or os.environ.get('CREATE_TEST_USERS') == 'true':
            logger.info("Creating test users...")
            test_users = create_test_users()
            logger.info(f"Created {len(test_users)} test users")

        logger.info("User management system setup completed successfully!")

        print("\n" + "="*60)
        print("USER MANAGEMENT SYSTEM SETUP COMPLETE")
        print("="*60)
        print(f"Admin Email: {admin_email}")
        print(f"Admin Username: {admin_username}")
        print(f"Admin Password: {admin_password}")
        print("\nIMPORTANT: Change the admin password after first login!")
        print("="*60)

        return True

    except Exception as e:
        logger.error(f"Setup failed: {e}")
        print(f"\nSETUP FAILED: {e}")
        return False

def reset_user_system():
    """Reset the user system (WARNING: Deletes all data)"""
    response = input("This will DELETE ALL USER DATA. Are you sure? (yes/no): ")
    if response.lower() != 'yes':
        print("Reset cancelled")
        return

    try:
        logger.info("Resetting user management system...")

        # Drop all tables
        db_manager.drop_tables()
        logger.info("All tables dropped")

        # Recreate tables
        init_database()
        logger.info("Tables recreated")

        print("User system reset completed!")

    except Exception as e:
        logger.error(f"Reset failed: {e}")
        print(f"RESET FAILED: {e}")

def show_help():
    """Show help information"""
    print("AI Stock Trading - User Management System Setup")
    print("=" * 50)
    print("Commands:")
    print("  setup     - Initialize the user management system")
    print("  reset     - Reset the system (deletes all data)")
    print("  help      - Show this help message")
    print("\nEnvironment Variables:")
    print("  ADMIN_EMAIL       - Admin user email (default: admin@aitrading.com)")
    print("  ADMIN_USERNAME    - Admin username (default: admin)")
    print("  ADMIN_PASSWORD    - Admin password (default: AdminPassword123!)")
    print("  ADMIN_FIRST_NAME  - Admin first name (default: System)")
    print("  ADMIN_LAST_NAME   - Admin last name (default: Administrator)")
    print("  CREATE_TEST_USERS - Create test users (default: false)")
    print("  DATABASE_URL      - Database connection URL")
    print("  JWT_SECRET_KEY    - JWT secret key for authentication")

if __name__ == '__main__':
    command = sys.argv[1] if len(sys.argv) > 1 else 'help'

    if command == 'setup':
        success = setup_user_system()
        sys.exit(0 if success else 1)
    elif command == 'reset':
        reset_user_system()
    elif command == 'help':
        show_help()
    else:
        print(f"Unknown command: {command}")
        show_help()
        sys.exit(1)