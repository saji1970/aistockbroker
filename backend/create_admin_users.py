#!/usr/bin/env python3
"""
Script to create admin users for the AI Stock Trading platform
"""

import os
import sys
from datetime import datetime, timezone

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager, init_database
from models import User, UserRole, UserStatus

def create_admin_user(email, username, password, first_name=None, last_name=None):
    """Create an admin user"""
    with db_manager.get_session() as session:
        try:
            # Check if admin user already exists
            existing_user = session.query(User).filter(
                (User.email == email.lower()) | (User.username == username)
            ).first()

            if existing_user:
                print(f"User already exists: {existing_user.email}")
                return {
                    'id': existing_user.id,
                    'email': existing_user.email,
                    'username': existing_user.username,
                    'role': existing_user.role.value if existing_user.role else None,
                    'exists': True
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

            print(f"Admin user created: {admin_user.email}")
            return {
                'id': admin_user.id,
                'email': admin_user.email,
                'username': admin_user.username,
                'role': admin_user.role.value if admin_user.role else None,
                'exists': False
            }

        except Exception as e:
            print(f"Error creating admin user: {e}")
            raise

def main():
    """Main function to create the admin users"""
    try:
        print("Initializing database...")
        init_database()

        print("Creating admin users...")

        # Create first admin user: saji@aitrader.com
        print("\n--- Creating User 1 ---")
        user1 = create_admin_user(
            email="saji@aitrader.com",
            username="saji",
            password="sajiai123@",
            first_name="Saji",
            last_name="Admin"
        )

        # Create second admin user: ranjit@aitrader.com
        print("\n--- Creating User 2 ---")
        user2 = create_admin_user(
            email="ranjit@aitrader.com",
            username="ranjit",
            password="ranjitai123@",
            first_name="Ranjit",
            last_name="Admin"
        )

        print("\n" + "="*60)
        print("ADMIN USERS CREATION SUMMARY")
        print("="*60)

        print(f"User 1: {user1['email']}")
        print(f"  Username: {user1['username']}")
        print(f"  Status: {'Already existed' if user1['exists'] else 'Created successfully'}")
        print(f"  Role: {user1['role']}")

        print(f"\nUser 2: {user2['email']}")
        print(f"  Username: {user2['username']}")
        print(f"  Status: {'Already existed' if user2['exists'] else 'Created successfully'}")
        print(f"  Role: {user2['role']}")

        print("\nLogin Credentials:")
        print("User 1: saji@aitrader.com / sajiai123@")
        print("User 2: ranjit@aitrader.com / ranjitai123@")
        print("="*60)

    except Exception as e:
        print(f"Failed to create admin users: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()