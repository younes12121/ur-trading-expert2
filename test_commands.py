"""
Command Testing Script
Tests all Telegram bot commands programmatically
"""

import sys
import os
import asyncio
from typing import Dict, List

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock Telegram Update and Context for testing
class MockUpdate:
    def __init__(self, user_id: int, command: str, args: List[str] = None):
        self.effective_user = MockUser(user_id)
        self.message = MockMessage(command, args or [])
        self._replies = []

class MockUser:
    def __init__(self, user_id: int):
        self.id = user_id
        self.username = f"test_user_{user_id}"
        self.first_name = "Test"
        self.last_name = "User"

class MockMessage:
    def __init__(self, command: str, args: List[str]):
        self.text = f"/{command} {' '.join(args)}" if args else f"/{command}"
        self._replies = []
    
    async def reply_text(self, text: str, parse_mode: str = None):
        self._replies.append({
            'text': text,
            'parse_mode': parse_mode,
            'timestamp': asyncio.get_event_loop().time()
        })
        return True

class MockContext:
    def __init__(self, args: List[str] = None):
        self.args = args or []


class CommandTester:
    """Test all bot commands"""

    def __init__(self):
        self.test_user_id = 999999
        self.results = []
    
    async def test_command(self, command_name: str, command_func, args: List[str] = None):
        """Test a single command"""
        try:
            update = MockUpdate(self.test_user_id, command_name, args)
            context = MockContext(args)
            
            # Import and set up required dependencies
            from user_manager import UserManager
            user_manager = UserManager()
            
            # Set user to premium for testing
            user_manager.set_user_tier(self.test_user_id, 'premium')
            
            # Run command
            await command_func(update, context)
            
            # Check if command replied
            if update.message._replies:
                reply = update.message._replies[0]
                return {
                    'command': command_name,
                    'args': args or [],
                    'status': 'success',
                    'reply_length': len(reply['text']),
                    'has_content': len(reply['text']) > 0
                }
            else:
                return {
                    'command': command_name,
                    'args': args or [],
                    'status': 'no_reply',
                    'error': 'Command did not reply'
                }
        except Exception as e:
            return {
                'command': command_name,
                'args': args or [],
                'status': 'error',
                'error': str(e)
            }
    
    async def test_all_commands(self):
        """Test all commands"""
        print("Testing All Bot Commands...\n")
        
        # Import command handlers
        try:
            import telegram_bot
        except ImportError:
            print("❌ Cannot import telegram_bot. Make sure you're in the correct directory.")
            return
        
        commands_to_test = [
            # Educational
            ('explain', 'explain_command', ['1']),
            ('learn', 'learn_command', []),
            ('glossary', 'glossary_command', ['RSI']),
            ('strategy', 'strategy_command', []),
            ('mistakes', 'mistakes_command', []),
            ('tutorials', 'tutorials_command', []),
            
            # Notifications
            ('notifications', 'notifications_command', []),
            ('pricealert', 'pricealert_command', ['EURUSD', '1.1000']),
            ('sessionalerts', 'sessionalerts_command', []),
            
            # Subscription
            ('subscribe', 'subscribe_command', []),
            ('billing', 'billing_command', []),
            
            # Community
            ('profile', 'profile_command', []),
            ('follow', 'follow_command', []),
            ('leaderboard', 'leaderboard_command', []),
            ('rate', 'rate_command', ['1', '5']),
            ('poll', 'poll_command', ['1']),
            ('success', 'success_command', []),
            ('referral', 'referral_command', []),
            
            # Broker
            ('broker', 'broker_command', []),
            ('paper', 'paper_command', []),
            
            # AI Features
            ('aipredict', 'ai_predict_command', ['EURUSD']),
            ('sentiment', 'sentiment_command', ['BTC']),
            ('smartmoney', 'smartmoney_command', ['EURUSD']),
            ('orderflow', 'orderflow_command', ['EURUSD']),
            ('marketmaker', 'marketmaker_command', ['EURUSD']),
            ('volumeprofile', 'volumeprofile_command', ['EURUSD']),
        ]
        
        results = []
        for cmd_name, cmd_func_name, args in commands_to_test:
            try:
                cmd_func = getattr(telegram_bot, cmd_func_name)
                result = await self.test_command(cmd_name, cmd_func, args)
                results.append(result)
                
                status_emoji = {
                    'success': '✅',
                    'no_reply': '⚠️',
                    'error': '❌'
                }.get(result['status'], '❓')
                
                print(f"{status_emoji} /{cmd_name} {' '.join(args) if args else ''}")
                if result['status'] == 'error':
                    print(f"   Error: {result.get('error', 'Unknown')}")
            except AttributeError:
                print(f"❌ /{cmd_name} - Command function not found")
                results.append({
                    'command': cmd_name,
                    'status': 'not_found',
                    'error': f'Function {cmd_func_name} not found'
                })
            except Exception as e:
                print(f"💥 /{cmd_name} - Exception: {str(e)}")
                results.append({
                    'command': cmd_name,
                    'status': 'exception',
                    'error': str(e)
                })
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 COMMAND TEST SUMMARY")
        print("=" * 60)
        
        total = len(results)
        success = sum(1 for r in results if r['status'] == 'success')
        errors = sum(1 for r in results if r['status'] in ['error', 'exception'])
        no_reply = sum(1 for r in results if r['status'] == 'no_reply')
        
        print(f"\nTotal Commands: {total}")
        print(f"✅ Success: {success}")
        print(f"⚠️ No Reply: {no_reply}")
        print(f"❌ Errors: {errors}")
        print(f"Success Rate: {(success/total*100):.1f}%")
        
        return results


async def main():
    tester = CommandTester()
    await tester.test_all_commands()


if __name__ == "__main__":
    asyncio.run(main())

