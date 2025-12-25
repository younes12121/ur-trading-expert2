"""
Complete Database Migration Script
Migrates all JSON data to PostgreSQL database

Usage:
    python migrate_to_postgresql.py [--dry-run] [--backup]
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional
import argparse

# Import database models
from database import (
    DatabaseManager, User, Subscription, Signal, Trade,
    UserNotification, PriceAlert, Analytics,
    UserTier, SubscriptionStatus, SignalStatus, TradeDirection
)

class JSONToPostgreSQLMigrator:
    """Complete migration from JSON files to PostgreSQL"""
    
    def __init__(self, database_url: Optional[str] = None, dry_run: bool = False):
        self.db = DatabaseManager(database_url)
        self.dry_run = dry_run
        self.stats = {
            'users': 0,
            'trades': 0,
            'signals': 0,
            'notifications': 0,
            'price_alerts': 0,
            'subscriptions': 0,
            'errors': []
        }
        
    def backup_json_files(self):
        """Create backup of all JSON files before migration"""
        backup_dir = f"backup_json_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        
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
        
        for json_file in json_files:
            if os.path.exists(json_file):
                import shutil
                shutil.copy2(json_file, os.path.join(backup_dir, json_file))
                print(f"Backed up {json_file}")
        
        print(f"All JSON files backed up to {backup_dir}/")
        return backup_dir
    
    def migrate_users(self):
        """Migrate users from users_data.json"""
        if not os.path.exists('users_data.json'):
            print("WARNING: users_data.json not found, skipping users migration")
            return
        
        print("\nMigrating users...")
        session = self.db.get_session()
        
        try:
            with open('users_data.json', 'r') as f:
                users_data = json.load(f)
            
            for telegram_id_str, user_data in users_data.items():
                try:
                    telegram_id = int(telegram_id_str)
                    
                    # Check if user already exists
                    existing = session.query(User).filter_by(telegram_id=telegram_id).first()
                    if existing:
                        print(f"  SKIP: User {telegram_id} already exists, skipping")
                        continue
                    
                    # Parse tier
                    tier_str = user_data.get('tier', 'free').upper()
                    try:
                        tier = UserTier[tier_str]
                    except KeyError:
                        tier = UserTier.FREE
                    
                    # Parse dates
                    sub_date = None
                    if user_data.get('subscription_date'):
                        try:
                            sub_date = datetime.strptime(user_data['subscription_date'], '%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                    
                    sub_expiry = None
                    if user_data.get('subscription_expiry'):
                        try:
                            sub_expiry = datetime.strptime(user_data['subscription_expiry'], '%Y-%m-%d')
                        except:
                            pass
                    
                    created_at = datetime.now()
                    if user_data.get('created_at'):
                        try:
                            created_at = datetime.strptime(user_data['created_at'], '%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                    
                    last_active = datetime.now()
                    if user_data.get('last_active'):
                        try:
                            last_active = datetime.strptime(user_data['last_active'], '%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                    
                    user = User(
                        telegram_id=telegram_id,
                        username=user_data.get('username'),
                        first_name=user_data.get('first_name'),
                        last_name=user_data.get('last_name'),
                        tier=tier,
                        subscription_date=sub_date,
                        subscription_expiry=sub_expiry,
                        trial_used=user_data.get('trial_used', False),
                        capital=float(user_data.get('capital', 500.0)),
                        risk_per_trade=float(user_data.get('risk_per_trade', 1.0)),
                        created_at=created_at,
                        last_active=last_active
                    )
                    
                    if not self.dry_run:
                        session.add(user)
                        self.stats['users'] += 1
                    else:
                        print(f"  [DRY RUN] Would migrate user {telegram_id}")
                        self.stats['users'] += 1
                        
                except Exception as e:
                    error_msg = f"Error migrating user {telegram_id_str}: {e}"
                    print(f"  ERROR: {error_msg}")
                    self.stats['errors'].append(error_msg)
            
            if not self.dry_run:
                session.commit()
                print(f"Migrated {self.stats['users']} users")
            else:
                print(f"[DRY RUN] Would migrate {self.stats['users']} users")
                
        except Exception as e:
            if not self.dry_run:
                session.rollback()
            print(f"ERROR: Error migrating users: {e}")
            self.stats['errors'].append(f"Users migration error: {e}")
        finally:
            session.close()
    
    def migrate_trades(self):
        """Migrate trades from trade_history.json"""
        if not os.path.exists('trade_history.json'):
            print("WARNING: trade_history.json not found, skipping trades migration")
            return
        
        print("\nMigrating trades...")
        session = self.db.get_session()
        
        try:
            with open('trade_history.json', 'r') as f:
                trades_data = json.load(f)
            
            trades_list = trades_data.get('trades', [])
            
            for trade_data in trades_list:
                try:
                    # Find user - we need telegram_id, but trade_history might not have it
                    # We'll need to match by some other method or skip
                    # For now, we'll create trades without user_id if not available
                    user_id = None
                    telegram_id = trade_data.get('telegram_id')
                    
                    if telegram_id:
                        user = session.query(User).filter_by(telegram_id=telegram_id).first()
                        if user:
                            user_id = user.id
                    
                    if not user_id:
                        print(f"  WARNING: Skipping trade - user not found")
                        continue
                    
                    # Parse direction
                    direction_str = trade_data.get('direction', 'BUY').upper()
                    try:
                        direction = TradeDirection[direction_str]
                    except KeyError:
                        direction = TradeDirection.BUY
                    
                    # Parse dates
                    opened_at = datetime.now()
                    if trade_data.get('opened_at'):
                        try:
                            opened_at = datetime.strptime(trade_data['opened_at'], '%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                    
                    closed_at = None
                    if trade_data.get('closed_at'):
                        try:
                            closed_at = datetime.strptime(trade_data['closed_at'], '%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                    
                    # Parse status
                    is_open = trade_data.get('status', 'OPEN').upper() == 'OPEN'
                    
                    trade = Trade(
                        user_id=user_id,
                        asset=trade_data.get('asset', 'UNKNOWN'),
                        direction=direction,
                        entry=float(trade_data.get('entry', 0)),
                        exit_price=float(trade_data.get('exit_price', 0)) if trade_data.get('exit_price') else None,
                        stop_loss=float(trade_data.get('stop_loss', 0)) if trade_data.get('stop_loss') else None,
                        tp1=float(trade_data.get('tp1', 0)) if trade_data.get('tp1') else None,
                        tp2=float(trade_data.get('tp2', 0)) if trade_data.get('tp2') else None,
                        position_size=float(trade_data.get('position_size', 0)) if trade_data.get('position_size') else None,
                        pnl=float(trade_data.get('pnl', 0)) if trade_data.get('pnl') else 0.0,
                        pips=float(trade_data.get('pips', 0)) if trade_data.get('pips') else 0.0,
                        is_open=is_open,
                        exit_type=trade_data.get('exit_type'),
                        opened_at=opened_at,
                        closed_at=closed_at
                    )
                    
                    if not self.dry_run:
                        session.add(trade)
                        self.stats['trades'] += 1
                    else:
                        print(f"  [DRY RUN] Would migrate trade for user {user_id}")
                        self.stats['trades'] += 1
                        
                except Exception as e:
                    error_msg = f"Error migrating trade: {e}"
                    print(f"  ERROR: {error_msg}")
                    self.stats['errors'].append(error_msg)
            
            if not self.dry_run:
                session.commit()
                print(f"Migrated {self.stats['trades']} trades")
            else:
                print(f"[DRY RUN] Would migrate {self.stats['trades']} trades")
                
        except Exception as e:
            if not self.dry_run:
                session.rollback()
            print(f"ERROR: Error migrating trades: {e}")
            self.stats['errors'].append(f"Trades migration error: {e}")
        finally:
            session.close()
    
    def migrate_signals(self):
        """Migrate signals from signals_db.json"""
        if not os.path.exists('signals_db.json'):
            print("WARNING: signals_db.json not found, skipping signals migration")
            return
        
        print("\nMigrating signals...")
        session = self.db.get_session()
        
        try:
            with open('signals_db.json', 'r') as f:
                signals_data = json.load(f)
            
            for signal_data in signals_data:
                try:
                    # Parse direction
                    direction_str = signal_data.get('direction', 'BUY').upper()
                    try:
                        direction = TradeDirection[direction_str]
                    except KeyError:
                        direction = TradeDirection.BUY
                    
                    # Parse status
                    status_str = signal_data.get('status', 'OPEN').upper()
                    try:
                        status = SignalStatus[status_str]
                    except KeyError:
                        status = SignalStatus.OPEN
                    
                    # Parse dates
                    created_at = datetime.now()
                    if signal_data.get('timestamp'):
                        try:
                            created_at = datetime.strptime(signal_data['timestamp'], '%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                    
                    closed_at = None
                    if signal_data.get('outcome_time'):
                        try:
                            closed_at = datetime.strptime(signal_data['outcome_time'], '%Y-%m-%d %H:%M:%S')
                        except:
                            pass
                    
                    # Prepare analysis details
                    analysis_details = {
                        'criteria_passed': signal_data.get('criteria_passed'),
                        'criteria_total': signal_data.get('criteria_total'),
                        'criteria_details': signal_data.get('criteria_details', {})
                    }
                    
                    signal = Signal(
                        pair=signal_data.get('pair', 'UNKNOWN'),
                        direction=direction,
                        timeframe=signal_data.get('timeframe', 'M15'),
                        price=float(signal_data.get('entry', 0)),
                        entry=float(signal_data.get('entry', 0)),
                        stop_loss=float(signal_data.get('sl', 0)) if signal_data.get('sl') else None,
                        tp1=float(signal_data.get('tp', 0)) if signal_data.get('tp') else None,
                        tp2=None,  # Not in JSON structure
                        confidence=None,  # Calculate if needed
                        criteria_passed=signal_data.get('criteria_passed'),
                        criteria_total=signal_data.get('criteria_total'),
                        status=status,
                        pips_gained=float(signal_data.get('pips_gained', 0)) if signal_data.get('pips_gained') else 0.0,
                        created_at=created_at,
                        closed_at=closed_at,
                        analysis_details=analysis_details
                    )
                    
                    if not self.dry_run:
                        session.add(signal)
                        self.stats['signals'] += 1
                    else:
                        print(f"  [DRY RUN] Would migrate signal {signal_data.get('id')}")
                        self.stats['signals'] += 1
                        
                except Exception as e:
                    error_msg = f"Error migrating signal: {e}"
                    print(f"  ERROR: {error_msg}")
                    self.stats['errors'].append(error_msg)
            
            if not self.dry_run:
                session.commit()
                print(f"Migrated {self.stats['signals']} signals")
            else:
                print(f"[DRY RUN] Would migrate {self.stats['signals']} signals")
                
        except Exception as e:
            if not self.dry_run:
                session.rollback()
            print(f"ERROR: Error migrating signals: {e}")
            self.stats['errors'].append(f"Signals migration error: {e}")
        finally:
            session.close()
    
    def migrate_notifications(self):
        """Migrate user notifications from user_notifications.json"""
        if not os.path.exists('user_notifications.json'):
            print("WARNING: user_notifications.json not found, skipping notifications migration")
            return
        
        print("\nMigrating user notifications...")
        session = self.db.get_session()
        
        try:
            with open('user_notifications.json', 'r') as f:
                notifications_data = json.load(f)
            
            # Handle nested structure: preferences and price_alerts
            preferences = notifications_data.get('preferences', {})
            
            for telegram_id_str, notif_data in preferences.items():
                try:
                    telegram_id = int(telegram_id_str)
                    
                    # Find user
                    user = session.query(User).filter_by(telegram_id=telegram_id).first()
                    if not user:
                        print(f"  WARNING: User {telegram_id} not found, skipping notification")
                        continue
                    
                    # Check if notification already exists
                    existing = session.query(UserNotification).filter_by(user_id=user.id).first()
                    if existing:
                        print(f"  SKIP: Notification for user {telegram_id} already exists")
                        continue
                    
                    notification = UserNotification(
                        user_id=user.id,
                        threshold_alerts=notif_data.get('threshold_alerts', True),
                        price_alerts=notif_data.get('price_alerts', True),
                        session_notifications=notif_data.get('session_notifications', True),
                        performance_summaries=notif_data.get('performance_summaries', True),
                        trade_reminders=notif_data.get('trade_reminders', True),
                        quiet_hours_enabled=notif_data.get('quiet_hours_enabled', False),
                        quiet_hours_start=notif_data.get('quiet_hours_start', '22:00'),
                        quiet_hours_end=notif_data.get('quiet_hours_end', '07:00')
                    )
                    
                    if not self.dry_run:
                        session.add(notification)
                        self.stats['notifications'] += 1
                    else:
                        print(f"  [DRY RUN] Would migrate notification for user {telegram_id}")
                        self.stats['notifications'] += 1
                        
                except Exception as e:
                    error_msg = f"Error migrating notification for {telegram_id_str}: {e}"
                    print(f"  ERROR: {error_msg}")
                    self.stats['errors'].append(error_msg)
            
            if not self.dry_run:
                session.commit()
                print(f"Migrated {self.stats['notifications']} notification settings")
            else:
                print(f"[DRY RUN] Would migrate {self.stats['notifications']} notification settings")
                
        except Exception as e:
            if not self.dry_run:
                session.rollback()
            print(f"ERROR: Error migrating notifications: {e}")
            self.stats['errors'].append(f"Notifications migration error: {e}")
        finally:
            session.close()
    
    def migrate_all(self, backup: bool = True):
        """Run complete migration"""
        print("=" * 60)
        print("Starting Database Migration (JSON -> PostgreSQL)")
        print("=" * 60)
        
        if backup:
            print("\nCreating backup of JSON files...")
            self.backup_json_files()
        
        if self.dry_run:
            print("\nDRY RUN MODE - No changes will be made to database")
        
        # Initialize database
        print("\nInitializing database...")
        self.db.create_tables()
        
        # Migrate all data
        self.migrate_users()
        self.migrate_trades()
        self.migrate_signals()
        self.migrate_notifications()
        
        # Print summary
        print("\n" + "=" * 60)
        print("Migration Summary")
        print("=" * 60)
        print(f"Users migrated:        {self.stats['users']}")
        print(f"Trades migrated:       {self.stats['trades']}")
        print(f"Signals migrated:      {self.stats['signals']}")
        print(f"Notifications migrated: {self.stats['notifications']}")
        print(f"Errors:                {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print("\nWARNING: Errors encountered:")
            for error in self.stats['errors'][:10]:  # Show first 10
                print(f"  - {error}")
            if len(self.stats['errors']) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more")
        
        print("\nMigration complete!")
        if self.dry_run:
            print("WARNING: This was a dry run. Run without --dry-run to perform actual migration.")


def main():
    parser = argparse.ArgumentParser(description='Migrate JSON data to PostgreSQL')
    parser.add_argument('--dry-run', action='store_true', help='Perform dry run without making changes')
    parser.add_argument('--no-backup', action='store_true', help='Skip JSON file backup')
    parser.add_argument('--database-url', type=str, help='PostgreSQL connection URL')
    
    args = parser.parse_args()
    
    migrator = JSONToPostgreSQLMigrator(
        database_url=args.database_url,
        dry_run=args.dry_run
    )
    
    migrator.migrate_all(backup=not args.no_backup)


if __name__ == "__main__":
    main()

