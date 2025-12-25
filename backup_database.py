#!/usr/bin/env python3
"""
Automated Database Backup Script
Creates daily backups of PostgreSQL database for Railway deployment
"""

import os
import sys
import subprocess
from datetime import datetime
import json

def get_database_url():
    """Get database URL from environment"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)
    return db_url

def create_backup_directory():
    """Create backup directory if it doesn't exist"""
    backup_dir = os.getenv('BACKUP_DIR', 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir

def backup_postgresql(db_url, backup_dir):
    """Create PostgreSQL backup using pg_dump"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'db_backup_{timestamp}.sql')
    
    # Parse database URL
    # Format: postgresql://user:password@host:port/database
    try:
        # Extract components from URL
        url_parts = db_url.replace('postgresql://', '').split('@')
        if len(url_parts) != 2:
            raise ValueError("Invalid DATABASE_URL format")
        
        auth_part = url_parts[0]
        host_part = url_parts[1]
        
        user, password = auth_part.split(':')
        host_port, database = host_part.split('/')
        
        if ':' in host_port:
            host, port = host_port.split(':')
        else:
            host = host_port
            port = '5432'
        
        # Use pg_dump to create backup
        # Note: pg_dump must be installed on the system
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        cmd = [
            'pg_dump',
            '-h', host,
            '-p', port,
            '-U', user,
            '-d', database,
            '-F', 'c',  # Custom format (compressed)
            '-f', backup_file
        ]
        
        print(f"Creating backup: {backup_file}")
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            file_size = os.path.getsize(backup_file) / (1024 * 1024)  # MB
            print(f"Backup created successfully: {backup_file} ({file_size:.2f} MB)")
            return backup_file
        else:
            print(f"ERROR: Backup failed: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"ERROR: Failed to create backup: {e}")
        # Fallback: Try using psql with COPY commands
        return backup_fallback(db_url, backup_file)

def backup_fallback(db_url, backup_file):
    """Fallback backup method using Python database connection"""
    try:
        from database import DatabaseManager
        from sqlalchemy import text
        
        db = DatabaseManager(db_url)
        session = db.get_session()
        
        # Get table names
        result = session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = [row[0] for row in result]
        
        backup_data = {}
        for table in tables:
            result = session.execute(text(f"SELECT * FROM {table}"))
            rows = [dict(row._mapping) for row in result]
            backup_data[table] = rows
        
        session.close()
        
        # Save as JSON (less efficient but works without pg_dump)
        json_file = backup_file.replace('.sql', '.json')
        with open(json_file, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        file_size = os.path.getsize(json_file) / (1024 * 1024)  # MB
        print(f"Backup created (JSON format): {json_file} ({file_size:.2f} MB)")
        return json_file
        
    except Exception as e:
        print(f"ERROR: Fallback backup also failed: {e}")
        return None

def cleanup_old_backups(backup_dir, retention_days=30):
    """Remove backups older than retention period"""
    try:
        retention_seconds = retention_days * 24 * 60 * 60
        current_time = datetime.now().timestamp()
        
        removed_count = 0
        for filename in os.listdir(backup_dir):
            if filename.startswith('db_backup_'):
                filepath = os.path.join(backup_dir, filename)
                file_time = os.path.getmtime(filepath)
                
                if current_time - file_time > retention_seconds:
                    os.remove(filepath)
                    removed_count += 1
                    print(f"Removed old backup: {filename}")
        
        if removed_count > 0:
            print(f"Cleaned up {removed_count} old backup(s)")
        else:
            print("No old backups to clean up")
            
    except Exception as e:
        print(f"WARNING: Failed to clean up old backups: {e}")

def main():
    """Main backup function"""
    print("=" * 60)
    print("Database Backup Script")
    print("=" * 60)
    
    # Get configuration
    db_url = get_database_url()
    backup_dir = create_backup_directory()
    retention_days = int(os.getenv('BACKUP_RETENTION_DAYS', 30))
    
    print(f"Backup directory: {backup_dir}")
    print(f"Retention period: {retention_days} days")
    print()
    
    # Create backup
    backup_file = backup_postgresql(db_url, backup_dir)
    
    if backup_file:
        # Cleanup old backups
        cleanup_old_backups(backup_dir, retention_days)
        
        print()
        print("=" * 60)
        print("Backup completed successfully")
        print("=" * 60)
        return 0
    else:
        print()
        print("=" * 60)
        print("Backup failed")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
