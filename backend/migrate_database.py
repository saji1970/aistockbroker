#!/usr/bin/env python3
"""
Database Migration Script
Adds agent-specific columns to existing tables and creates new agent tables
"""

import os
import sys
import sqlite3
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import db_manager

def migrate_user_table():
    """Add new columns to users table"""
    try:
        # Connect to SQLite database directly for migration
        db_path = os.path.join(os.path.dirname(__file__), 'trading_platform.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]

        # Add assigned_agent_id column
        if 'assigned_agent_id' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN assigned_agent_id INTEGER')
            print("Added assigned_agent_id column to users table")

        # Add agent_commission_rate column
        if 'agent_commission_rate' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN agent_commission_rate REAL DEFAULT 0.02')
            print("Added agent_commission_rate column to users table")

        conn.commit()
        conn.close()

        return True
    except Exception as e:
        print(f"Error migrating user table: {e}")
        return False

def create_agent_tables():
    """Create all agent-related tables"""
    try:
        # Import models to register them
        from models.user import Base
        import models.agent_models

        # Create all tables
        Base.metadata.create_all(bind=db_manager.engine)
        print("Created all agent tables")

        return True
    except Exception as e:
        print(f"Error creating agent tables: {e}")
        return False

def main():
    """Main migration function"""
    print("Starting database migration...")
    print("=" * 40)

    # Step 1: Migrate existing user table
    print("\nStep 1: Migrating user table")
    if not migrate_user_table():
        print("Migration failed at user table")
        return False

    # Step 2: Create new agent tables
    print("\nStep 2: Creating agent tables")
    if not create_agent_tables():
        print("Migration failed at agent table creation")
        return False

    print("\n" + "=" * 40)
    print("DATABASE MIGRATION COMPLETE!")
    print("You can now run setup_agents_clean.py")

    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)