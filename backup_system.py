"""
Automated Backup System
Creates regular backups of database and JSON files
"""

import os
import shutil
import json
import subprocess
from datetime import datetime, timedelta
from typing import List, Optional
import gzip
import tarfile

class BackupManager:
    """Manages automated backups of database and files"""
    
    def __init__(self, backup_dir: str = "backups", 
                 db_url: Optional[str] = None,
                 retention_days: int = 30):
        self.backup_dir = backup_dir
        self.db_url = db_url
        self.retention_days = retention_days
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create subdirectories
        self.db_backup_dir = os.path.join(backup_dir, 'database')
        self.json_backup_dir = os.path.join(backup_dir, 'json')
        os.makedirs(self.db_backup_dir, exist_ok=True)
        os.makedirs(self.json_backup_dir, exist_ok=True)
    
    def backup_database(self) -> str:
        """Backup PostgreSQL database using pg_dump"""
        if not self.db_url:
            print("⚠️  No database URL provided, skipping database backup")
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(self.db_backup_dir, f'db_backup_{timestamp}.sql.gz')
        
        try:
            # Parse database URL
            # Format: postgresql://user:password@host:port/database
            import re
            match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', self.db_url)
            if not match:
                print("❌ Invalid database URL format")
                return None
            
            user, password, host, port, database = match.groups()
            
            # Set PGPASSWORD environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = password
            
            # Create backup using pg_dump
            cmd = [
                'pg_dump',
                '-h', host,
                '-p', port,
                '-U', user,
                '-d', database,
                '--no-password',
                '--format=custom',
                '--file', backup_file.replace('.gz', '')
            ]
            
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Compress the backup
                with open(backup_file.replace('.gz', ''), 'rb') as f_in:
                    with gzip.open(backup_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Remove uncompressed file
                os.remove(backup_file.replace('.gz', ''))
                
                print(f"✅ Database backup created: {backup_file}")
                return backup_file
            else:
                print(f"❌ Database backup failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ Error backing up database: {e}")
            return None
    
    def backup_json_files(self) -> str:
        """Backup all JSON data files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(self.json_backup_dir, f'json_backup_{timestamp}.tar.gz')
        
        json_files = [
            'users_data.json',
            'trade_history.json',
            'signals_db.json',
            'user_notifications.json',
            'user_profiles.json',
            'community_data.json',
            'referral_data.json',
            'paper_trading.json',
            'sentiment_data.json',
            'broker_connections.json'
        ]
        
        try:
            with tarfile.open(backup_file, 'w:gz') as tar:
                for json_file in json_files:
                    if os.path.exists(json_file):
                        tar.add(json_file, arcname=json_file)
                        print(f"  ✅ Added {json_file} to backup")
            
            print(f"✅ JSON files backup created: {backup_file}")
            return backup_file
            
        except Exception as e:
            print(f"❌ Error backing up JSON files: {e}")
            return None
    
    def backup_all(self) -> Dict[str, str]:
        """Create all backups"""
        print("=" * 60)
        print("🔄 Starting backup process...")
        print("=" * 60)
        
        backups = {}
        
        # Backup database
        db_backup = self.backup_database()
        if db_backup:
            backups['database'] = db_backup
        
        # Backup JSON files
        json_backup = self.backup_json_files()
        if json_backup:
            backups['json'] = json_backup
        
        print("=" * 60)
        print("✅ Backup process complete!")
        print("=" * 60)
        
        return backups
    
    def cleanup_old_backups(self):
        """Remove backups older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        deleted_count = 0
        
        for backup_dir in [self.db_backup_dir, self.json_backup_dir]:
            if not os.path.exists(backup_dir):
                continue
            
            for filename in os.listdir(backup_dir):
                filepath = os.path.join(backup_dir, filename)
                
                # Extract timestamp from filename
                try:
                    # Format: db_backup_YYYYMMDD_HHMMSS.sql.gz
                    parts = filename.split('_')
                    if len(parts) >= 3:
                        date_str = parts[2]  # YYYYMMDD
                        time_str = parts[3].split('.')[0]  # HHMMSS
                        file_date = datetime.strptime(f"{date_str}_{time_str}", '%Y%m%d_%H%M%S')
                        
                        if file_date < cutoff_date:
                            os.remove(filepath)
                            deleted_count += 1
                            print(f"  🗑️  Deleted old backup: {filename}")
                except:
                    # If we can't parse the date, skip it
                    pass
        
        if deleted_count > 0:
            print(f"✅ Cleaned up {deleted_count} old backup(s)")
        else:
            print("✅ No old backups to clean up")
    
    def restore_database(self, backup_file: str) -> bool:
        """Restore database from backup"""
        if not self.db_url:
            print("❌ No database URL provided")
            return False
        
        try:
            # Decompress if needed
            if backup_file.endswith('.gz'):
                decompressed = backup_file.replace('.gz', '')
                with gzip.open(backup_file, 'rb') as f_in:
                    with open(decompressed, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_file = decompressed
            
            # Parse database URL
            import re
            match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', self.db_url)
            if not match:
                print("❌ Invalid database URL format")
                return False
            
            user, password, host, port, database = match.groups()
            
            # Set PGPASSWORD
            env = os.environ.copy()
            env['PGPASSWORD'] = password
            
            # Restore using pg_restore
            cmd = [
                'pg_restore',
                '-h', host,
                '-p', port,
                '-U', user,
                '-d', database,
                '--no-password',
                '--clean',
                '--if-exists',
                backup_file
            ]
            
            print(f"🔄 Restoring database from {backup_file}...")
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Database restored successfully")
                return True
            else:
                print(f"❌ Database restore failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error restoring database: {e}")
            return False
        finally:
            # Clean up decompressed file if we created it
            if backup_file.endswith('.sql') and os.path.exists(backup_file):
                if backup_file != os.path.basename(backup_file):
                    os.remove(backup_file)
    
    def list_backups(self) -> Dict[str, List[str]]:
        """List all available backups"""
        backups = {
            'database': [],
            'json': []
        }
        
        for backup_type in ['database', 'json']:
            backup_dir = os.path.join(self.backup_dir, backup_type)
            if os.path.exists(backup_dir):
                backups[backup_type] = sorted(os.listdir(backup_dir))
        
        return backups


def schedule_backups(backup_manager: BackupManager, interval_hours: int = 24):
    """Schedule regular backups (run in background thread)"""
    import threading
    import time
    
    def backup_loop():
        while True:
            try:
                backup_manager.backup_all()
                backup_manager.cleanup_old_backups()
            except Exception as e:
                print(f"❌ Error in backup loop: {e}")
            
            # Wait for next backup
            time.sleep(interval_hours * 3600)
    
    thread = threading.Thread(target=backup_loop, daemon=True)
    thread.start()
    return thread


if __name__ == "__main__":
    import sys
    
    backup_manager = BackupManager(
        db_url=os.getenv('DATABASE_URL'),
        retention_days=30
    )
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'backup':
            backup_manager.backup_all()
        elif command == 'cleanup':
            backup_manager.cleanup_old_backups()
        elif command == 'list':
            backups = backup_manager.list_backups()
            print("Database backups:")
            for backup in backups['database']:
                print(f"  - {backup}")
            print("\nJSON backups:")
            for backup in backups['json']:
                print(f"  - {backup}")
        elif command == 'restore' and len(sys.argv) > 2:
            backup_file = sys.argv[2]
            backup_manager.restore_database(backup_file)
        else:
            print("Usage:")
            print("  python backup_system.py backup    - Create backups")
            print("  python backup_system.py cleanup    - Clean old backups")
            print("  python backup_system.py list        - List backups")
            print("  python backup_system.py restore <file> - Restore database")
    else:
        backup_manager.backup_all()

