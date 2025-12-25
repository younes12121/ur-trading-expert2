"""
International Signal API
Manages signal generation for international markets including Asian currencies,
emerging markets, and additional crypto futures
"""

from typing import Dict, Optional, List
import logging
from datetime import datetime

# Import international signal generators
try:
    from International_Markets.Asian_Markets.cny_signal_generator import CNYSignalGenerator
    from International_Markets.Asian_Markets.jpy_signal_generator import JPYSignalGenerator
    from International_Markets.European_Markets.eur_signal_generator import EURSignalGenerator
    from International_Markets.European_Markets.gbp_signal_generator import GBPUSDGenerator
    from International_Markets.Pacific_Markets.aud_signal_generator import AUDUSDGenerator
    from International_Markets.Emerging_Markets.brl_signal_generator import BRLSignalGenerator
    from International_Markets.Crypto_Futures.eth_signal_generator import ETHSignalGenerator
    INTERNATIONAL_GENERATORS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"International signal generators not available: {e}")
    INTERNATIONAL_GENERATORS_AVAILABLE = False
    CNYSignalGenerator = None
    JPYSignalGenerator = None
    EURSignalGenerator = None
    GBPUSDGenerator = None
    AUDUSDGenerator = None
    BRLSignalGenerator = None
    ETHSignalGenerator = None

class InternationalSignalAPI:
    """API for generating signals across international markets"""

    def __init__(self, data_fetcher=None):
        self.data_fetcher = data_fetcher
        self.logger = logging.getLogger(__name__)

        # Initialize signal generators
        self.generators = {}
        if INTERNATIONAL_GENERATORS_AVAILABLE:
            self._initialize_generators()
        else:
            self.logger.warning("International signal generators not loaded")

        # Market configurations
        self.market_configs = {
            'CNY': {
                'generator': 'cny',
                'category': 'Asian Markets',
                'volatility': 'Low',
                'trading_hours': 'Asian Session',
                'description': 'Chinese Yuan - Major Asian economy currency'
            },
            'JPY': {
                'generator': 'jpy',
                'category': 'Asian Markets',
                'volatility': 'Very Low',
                'trading_hours': 'Asian Session',
                'description': 'Japanese Yen - Low volatility, safe-haven currency'
            },
            'EUR': {
                'generator': 'eur',
                'category': 'European Markets',
                'volatility': 'Medium',
                'trading_hours': 'European Session',
                'description': 'Euro - Major European currency, ECB influenced'
            },
            'GBP': {
                'generator': 'gbp',
                'category': 'European Markets',
                'volatility': 'Medium-High',
                'trading_hours': 'European Session',
                'description': 'British Pound - UK economy, BoE policy driven'
            },
            'AUD': {
                'generator': 'aud',
                'category': 'Pacific Markets',
                'volatility': 'Medium',
                'trading_hours': 'Asian/Pacific Session',
                'description': 'Australian Dollar - Commodity currency, RBA influenced'
            },
            'BRL': {
                'generator': 'brl',
                'category': 'Emerging Markets',
                'volatility': 'High',
                'trading_hours': 'Americas Session',
                'description': 'Brazilian Real - Emerging market with commodity exposure'
            },
            'ETH': {
                'generator': 'eth',
                'category': 'Crypto Futures',
                'volatility': 'Extreme',
                'trading_hours': '24/7',
                'description': 'Ethereum Futures - Smart contract platform cryptocurrency'
            }
        }

    def _initialize_generators(self):
        """Initialize all international signal generators"""
        try:
            self.generators['cny'] = CNYSignalGenerator(self.data_fetcher)
            self.generators['jpy'] = JPYSignalGenerator(self.data_fetcher)
            self.generators['eur'] = EURSignalGenerator(self.data_fetcher)
            self.generators['gbp'] = GBPUSDGenerator(self.data_fetcher)
            self.generators['aud'] = AUDUSDGenerator(self.data_fetcher)
            self.generators['brl'] = BRLSignalGenerator(self.data_fetcher)
            self.generators['eth'] = ETHSignalGenerator(self.data_fetcher)
            self.logger.info("International signal generators initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize international generators: {e}")

    def generate_signal(self, symbol: str) -> Dict:
        """Generate signal for international market symbol"""
        try:
            # Map symbol to generator
            generator_key = self._map_symbol_to_generator(symbol)
            if not generator_key:
                return self._error_signal(symbol, f"Unsupported international symbol: {symbol}")

            # Get generator
            generator = self.generators.get(generator_key)
            if not generator:
                return self._error_signal(symbol, f"Generator not available for: {symbol}")

            # Generate signal
            signal = generator.generate_signal()

            # Add international metadata
            signal['international'] = True
            signal['market_config'] = self.market_configs.get(symbol, {})

            return signal

        except Exception as e:
            self.logger.error(f"Error generating international signal for {symbol}: {e}")
            return self._error_signal(symbol, str(e))

    def get_available_symbols(self) -> List[str]:
        """Get list of available international symbols"""
        return list(self.market_configs.keys())

    def get_market_info(self, symbol: str) -> Dict:
        """Get market information for a symbol"""
        return self.market_configs.get(symbol, {})

    def get_all_market_info(self) -> Dict:
        """Get information for all international markets"""
        return self.market_configs

    def _map_symbol_to_generator(self, symbol: str) -> Optional[str]:
        """Map symbol to generator key"""
        symbol_mapping = {
            'CNY': 'cny',
            'USDCNY': 'cny',
            'CNYUSD': 'cny',
            'JPY': 'jpy',
            'USDJPY': 'jpy',
            'JPYUSD': 'jpy',
            'EUR': 'eur',
            'EURUSD': 'eur',
            'USDEUR': 'eur',
            'GBP': 'gbp',
            'GBPUSD': 'gbp',
            'USDGBP': 'gbp',
            'AUD': 'aud',
            'AUDUSD': 'aud',
            'USDAUD': 'aud',
            'BRL': 'brl',
            'USDBRL': 'brl',
            'BRLUSD': 'brl',
            'ETH': 'eth',
            'ETHUSD': 'eth',
            'ETH/USDT': 'eth'
        }

        return symbol_mapping.get(symbol.upper())

    def _error_signal(self, symbol: str, message: str) -> Dict:
        """Return error signal structure"""
        return {
            'symbol': symbol,
            'name': f'{symbol} International',
            'description': 'International Market Signal',
            'timestamp': datetime.now().isoformat(),
            'direction': 'ERROR',
            'confidence': 0,
            'message': message,
            'signal_quality': 'ERROR',
            'international': True,
            'error': True
        }

# Global instance for easy access
international_api = InternationalSignalAPI()

def get_international_signal(symbol: str) -> Dict:
    """Convenience function to get international signal"""
    return international_api.generate_signal(symbol)

def get_international_symbols() -> List[str]:
    """Convenience function to get available symbols"""
    return international_api.get_available_symbols()

def get_international_market_info(symbol: str) -> Dict:
    """Convenience function to get market info"""
    return international_api.get_market_info(symbol)

# Example usage and testing
if __name__ == "__main__":
    print("International Signal API Test")
    print("=" * 50)

    # Test available symbols
    symbols = get_international_symbols()
    print(f"Available International Symbols: {symbols}")

    # Test each symbol
    for symbol in symbols:
        print(f"\nTesting {symbol}:")
        try:
            signal = get_international_signal(symbol)
            print(f"  Direction: {signal.get('direction', 'N/A')}")
            print(f"  Confidence: {signal.get('confidence', 0)}%")
            print(f"  Quality: {signal.get('signal_quality', 'N/A')}")

            market_info = get_international_market_info(symbol)
            print(f"  Category: {market_info.get('category', 'Unknown')}")
            print(f"  Volatility: {market_info.get('volatility', 'Unknown')}")

        except Exception as e:
            print(f"  Error: {e}")

    print("\nInternational Signal API test completed!")
