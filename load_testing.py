"""
Load Testing Suite
Simulates 100+ concurrent users to test bot performance
"""

import asyncio
import aiohttp
import time
import json
from datetime import datetime
from typing import List, Dict
import statistics

class LoadTester:
    """Load testing for Telegram bot"""
    
    def __init__(self, bot_token: str, base_url: str = "https://api.telegram.org"):
        self.bot_token = bot_token
        self.base_url = base_url
        self.results = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'errors': []
        }
    
    async def simulate_command(self, command: str, user_id: int, 
                              session: aiohttp.ClientSession) -> Dict:
        """Simulate a bot command execution"""
        start_time = time.time()
        
        try:
            # Simulate sending command to bot via Telegram API
            # In real testing, you'd use the actual Telegram API
            url = f"{self.base_url}/bot{self.bot_token}/sendMessage"
            
            payload = {
                'chat_id': user_id,
                'text': f'/{command}',
                'parse_mode': 'HTML'
            }
            
            async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response_time = time.time() - start_time
                success = response.status == 200
                
                if success:
                    self.results['successful_requests'] += 1
                else:
                    self.results['failed_requests'] += 1
                    error_text = await response.text()
                    self.results['errors'].append({
                        'command': command,
                        'user_id': user_id,
                        'status': response.status,
                        'error': error_text[:200]
                    })
                
                self.results['response_times'].append(response_time)
                self.results['total_requests'] += 1
                
                return {
                    'success': success,
                    'response_time': response_time,
                    'status': response.status
                }
                
        except Exception as e:
            response_time = time.time() - start_time
            self.results['failed_requests'] += 1
            self.results['response_times'].append(response_time)
            self.results['errors'].append({
                'command': command,
                'user_id': user_id,
                'error': str(e)
            })
            
            return {
                'success': False,
                'response_time': response_time,
                'error': str(e)
            }
    
    async def simulate_user_session(self, user_id: int, 
                                   commands: List[str],
                                   session: aiohttp.ClientSession,
                                   delay_between_commands: float = 2.0):
        """Simulate a full user session with multiple commands"""
        for command in commands:
            await self.simulate_command(command, user_id, session)
            await asyncio.sleep(delay_between_commands)
    
    async def run_load_test(self, num_users: int = 100, 
                           commands_per_user: int = 5,
                           concurrent_limit: int = 50):
        """Run load test with specified number of users"""
        print("=" * 60)
        print(f"🚀 Starting Load Test")
        print(f"   Users: {num_users}")
        print(f"   Commands per user: {commands_per_user}")
        print(f"   Concurrent limit: {concurrent_limit}")
        print("=" * 60)
        
        # Common commands to test
        test_commands = [
            'start', 'help', 'btc', 'gold', 'eurusd', 'gbpusd',
            'analytics', 'profile', 'settings', 'news'
        ]
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            # Create semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(concurrent_limit)
            
            async def bounded_simulate(user_id):
                async with semaphore:
                    user_commands = test_commands[:commands_per_user]
                    await self.simulate_user_session(
                        user_id, 
                        user_commands, 
                        session,
                        delay_between_commands=1.0
                    )
            
            # Create tasks for all users
            tasks = [
                bounded_simulate(1000000 + i)  # Generate unique user IDs
                for i in range(num_users)
            ]
            
            # Run all tasks concurrently
            await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # Calculate statistics
        self.print_results(total_time)
    
    def print_results(self, total_time: float):
        """Print load test results"""
        print("\n" + "=" * 60)
        print("📊 Load Test Results")
        print("=" * 60)
        
        print(f"Total Requests:        {self.results['total_requests']}")
        print(f"Successful:            {self.results['successful_requests']}")
        print(f"Failed:                {self.results['failed_requests']}")
        print(f"Success Rate:          {(self.results['successful_requests'] / self.results['total_requests'] * 100):.2f}%")
        print(f"Total Time:            {total_time:.2f}s")
        print(f"Requests/Second:       {(self.results['total_requests'] / total_time):.2f}")
        
        if self.results['response_times']:
            print(f"\nResponse Time Statistics:")
            print(f"  Average:             {statistics.mean(self.results['response_times']):.3f}s")
            print(f"  Median:              {statistics.median(self.results['response_times']):.3f}s")
            print(f"  Min:                 {min(self.results['response_times']):.3f}s")
            print(f"  Max:                 {max(self.results['response_times']):.3f}s")
            print(f"  95th Percentile:     {self.percentile(self.results['response_times'], 95):.3f}s")
            print(f"  99th Percentile:     {self.percentile(self.results['response_times'], 99):.3f}s")
        
        if self.results['errors']:
            print(f"\n⚠️  Errors ({len(self.results['errors'])}):")
            error_types = {}
            for error in self.results['errors'][:20]:  # Show first 20
                error_type = error.get('error', 'Unknown')
                if isinstance(error_type, str) and len(error_type) > 50:
                    error_type = error_type[:50] + '...'
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            for error_type, count in list(error_types.items())[:10]:
                print(f"  - {error_type}: {count}")
        
        print("=" * 60)
        
        # Save results to file
        results_file = f"load_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': self.results,
                'total_time': total_time
            }, f, indent=2)
        
        print(f"✅ Results saved to {results_file}")
    
    @staticmethod
    def percentile(data: List[float], percentile: float) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


class StressTester:
    """Stress testing - gradually increase load"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.load_tester = LoadTester(bot_token)
    
    async def run_stress_test(self, start_users: int = 10, 
                            max_users: int = 200,
                            step: int = 10,
                            commands_per_user: int = 3):
        """Gradually increase load to find breaking point"""
        print("=" * 60)
        print("🔥 Starting Stress Test")
        print(f"   Starting with {start_users} users")
        print(f"   Increasing to {max_users} users")
        print(f"   Step size: {step}")
        print("=" * 60)
        
        current_users = start_users
        results = []
        
        while current_users <= max_users:
            print(f"\n📊 Testing with {current_users} users...")
            
            # Reset results
            self.load_tester.results = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'response_times': [],
                'errors': []
            }
            
            start_time = time.time()
            await self.load_tester.run_load_test(
                num_users=current_users,
                commands_per_user=commands_per_user,
                concurrent_limit=min(current_users, 50)
            )
            total_time = time.time() - start_time
            
            success_rate = (self.load_tester.results['successful_requests'] / 
                          max(self.load_tester.results['total_requests'], 1)) * 100
            
            avg_response_time = 0
            if self.load_tester.results['response_times']:
                avg_response_time = statistics.mean(self.load_tester.results['response_times'])
            
            results.append({
                'users': current_users,
                'success_rate': success_rate,
                'avg_response_time': avg_response_time,
                'total_time': total_time,
                'errors': len(self.load_tester.results['errors'])
            })
            
            print(f"   Success Rate: {success_rate:.2f}%")
            print(f"   Avg Response: {avg_response_time:.3f}s")
            
            # If success rate drops below 80%, we've found the breaking point
            if success_rate < 80:
                print(f"\n⚠️  Breaking point reached at {current_users} users")
                break
            
            current_users += step
            await asyncio.sleep(2)  # Brief pause between tests
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 Stress Test Summary")
        print("=" * 60)
        for result in results:
            print(f"Users: {result['users']:3d} | "
                  f"Success: {result['success_rate']:5.1f}% | "
                  f"Response: {result['avg_response_time']:.3f}s | "
                  f"Errors: {result['errors']}")
        print("=" * 60)


if __name__ == "__main__":
    import os
    import sys
    
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN environment variable not set")
        sys.exit(1)
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1]
        
        if test_type == 'load':
            num_users = int(sys.argv[2]) if len(sys.argv) > 2 else 100
            tester = LoadTester(bot_token)
            asyncio.run(tester.run_load_test(num_users=num_users))
        
        elif test_type == 'stress':
            tester = StressTester(bot_token)
            asyncio.run(tester.run_stress_test())
        
        else:
            print("Usage:")
            print("  python load_testing.py load [num_users]  - Run load test")
            print("  python load_testing.py stress            - Run stress test")
    else:
        # Default: run load test with 100 users
        tester = LoadTester(bot_token)
        asyncio.run(tester.run_load_test(num_users=100))

