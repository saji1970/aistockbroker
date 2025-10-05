#!/usr/bin/env python3
"""
Check for agent users in the database
"""

import sys
import os
sys.path.append('backend')

from database import db_manager
from models.user import User, UserRole

def check_agent_users():
    try:
        with db_manager.get_session() as session:
            users = session.query(User).filter(User.role == UserRole.AGENT).all()
            print(f'Found {len(users)} agent users:')
            for u in users:
                print(f'- {u.email} ({u.username}) - Status: {u.status.value}')
            
            # Also check all users
            all_users = session.query(User).all()
            print(f'\nTotal users: {len(all_users)}')
            for u in all_users:
                print(f'- {u.email} ({u.username}) - Role: {u.role.value} - Status: {u.status.value}')
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_agent_users()
