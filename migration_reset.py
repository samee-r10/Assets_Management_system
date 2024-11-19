# migration_reset.py
from app import create_app, db
from flask_migrate import Migrate, init, migrate, upgrade, stamp
from app.models import User, Inventory, Log  # Import your models
import os
import shutil

def reset_migrations():
    app = create_app()
    migrate = Migrate(app, db)
    
    with app.app_context():
        try:
            print("Starting migration reset process...")
            
            # Step 1: Remove existing migration folder
            if os.path.exists('migrations'):
                print("Removing existing migrations folder...")
                shutil.rmtree('migrations')
            
            # Step 2: Initialize fresh migrations
            print("Initializing new migrations...")
            init()
            
            # Step 3: Create a new migration
            print("Creating new migration...")
            migrate(message='fresh_start')
            
            # Step 4: Stamp the database with the new migration
            print("Stamping database...")
            stamp('head')
            
            # Step 5: Upgrade to the latest migration
            print("Upgrading database to latest migration...")
            upgrade()
            
            # Step 6: Verify database connection and tables
            print("\nVerifying database state...")
            tables = db.engine.table_names()
            print(f"Current tables in database: {', '.join(tables)}")
            
            print("\nMigration reset completed successfully!")
            
        except Exception as e:
            print(f"\nError during migration reset: {str(e)}")
            print("\nTroubleshooting steps:")
            print("1. Verify your database credentials in config")
            print("2. Make sure you have necessary permissions")
            print("3. Check if any processes are locking the database")
            print("\nDatabase connection details (for verification):")
            print(f"Host: {os.getenv('MYSQL_HOST')}")
            print(f"Database: {os.getenv('MYSQL_DB')}")
            print(f"User: {os.getenv('MYSQL_USER')}")

if __name__ == '__main__':
    reset_migrations()