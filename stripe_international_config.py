"""
Stripe International Configuration
Supports 40+ countries with local payment methods and multi-currency
"""

# Stripe supported countries (40+)
STRIPE_SUPPORTED_COUNTRIES = [
    'US', 'GB', 'CA', 'AU', 'NZ',  # English-speaking
    'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'AT', 'CH', 'SE', 'NO', 'DK', 'FI', 'PL', 'PT', 'IE',  # Europe
    'JP', 'KR', 'SG', 'HK', 'MY', 'TH', 'ID', 'PH', 'VN', 'TW',  # Asia Pacific
    'BR', 'MX', 'AR', 'CL', 'CO', 'PE',  # Latin America
    'AE', 'SA', 'IL', 'TR',  # Middle East
    'ZA', 'NG', 'KE',  # Africa
    'IN'  # South Asia
]

# Regional payment methods mapping
REGIONAL_PAYMENT_METHODS = {
    # Europe
    'NL': ['card', 'ideal'],  # Netherlands - iDEAL
    'BE': ['card', 'bancontact'],  # Belgium - Bancontact
    'DE': ['card', 'sofort'],  # Germany - Sofort
    'AT': ['card', 'eps'],  # Austria - EPS
    'PL': ['card', 'blik'],  # Poland - BLIK
    'IT': ['card', 'giropay'],  # Italy - Giropay
    
    # Asia
    'CN': ['card', 'alipay', 'wechat_pay'],  # China - Alipay, WeChat Pay
    'SG': ['card', 'grabpay'],  # Singapore - GrabPay
    'MY': ['card', 'fpx'],  # Malaysia - FPX
    'TH': ['card', 'promptpay'],  # Thailand - PromptPay
    'JP': ['card', 'konbini'],  # Japan - Konbini
    
    # Latin America
    'BR': ['card', 'boleto'],  # Brazil - Boleto
    'MX': ['card', 'oxxo'],  # Mexico - OXXO
    'AR': ['card', 'rapipago'],  # Argentina - Rapipago
    'CL': ['card', 'webpay'],  # Chile - Webpay
    
    # Middle East
    'AE': ['card', 'mada'],  # UAE - Mada
    'SA': ['card', 'mada'],  # Saudi Arabia - Mada
}

# Currency to country mapping
CURRENCY_COUNTRY_MAP = {
    'USD': ['US', 'PR', 'VI', 'GU', 'AS', 'MH', 'FM', 'PW'],
    'EUR': ['AT', 'BE', 'CY', 'EE', 'FI', 'FR', 'DE', 'GR', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PT', 'SK', 'SI', 'ES'],
    'GBP': ['GB', 'GG', 'JE', 'IM'],
    'JPY': ['JP'],
    'AUD': ['AU', 'KI', 'NR', 'TV'],
    'CAD': ['CA'],
    'CHF': ['CH', 'LI'],
    'CNY': ['CN'],
    'HKD': ['HK'],
    'SGD': ['SG'],
    'BRL': ['BR'],
    'MXN': ['MX'],
    'ARS': ['AR'],
    'INR': ['IN'],
    'KRW': ['KR'],
    'THB': ['TH'],
    'MYR': ['MY'],
    'IDR': ['ID'],
    'PHP': ['PH'],
    'VND': ['VN'],
    'AED': ['AE'],
    'SAR': ['SA'],
    'ZAR': ['ZA'],
    'NGN': ['NG'],
    'KES': ['KE'],
    'TRY': ['TR'],
    'ILS': ['IL'],
    'NZD': ['NZ'],
    'CLP': ['CL'],
    'COP': ['CO'],
    'PEN': ['PE'],
}

# Regional pricing adjustments (percentage of base USD price)
REGIONAL_PRICING_ADJUSTMENTS = {
    # Developed markets - slight discount
    'US': 1.0,  # Base
    'CA': 1.0,
    'GB': 0.95,  # 5% discount
    'AU': 1.05,  # 5% premium
    'NZ': 1.05,
    'SG': 1.0,
    'HK': 1.0,
    
    # Europe - adjusted for purchasing power
    'DE': 0.92,
    'FR': 0.92,
    'IT': 0.90,
    'ES': 0.88,
    'NL': 0.95,
    'BE': 0.95,
    'AT': 0.95,
    'CH': 1.10,  # Higher purchasing power
    'SE': 1.0,
    'NO': 1.05,
    'DK': 1.0,
    'FI': 1.0,
    
    # Asia - adjusted for local markets
    'JP': 0.95,
    'KR': 0.90,
    'CN': 0.70,  # Significant discount for China
    'IN': 0.50,  # Major discount for India
    'TH': 0.75,
    'MY': 0.80,
    'ID': 0.70,
    'PH': 0.70,
    'VN': 0.65,
    'TW': 0.90,
    
    # Latin America - adjusted for purchasing power
    'BR': 0.60,  # Significant discount
    'MX': 0.70,
    'AR': 0.65,
    'CL': 0.75,
    'CO': 0.70,
    'PE': 0.70,
    
    # Middle East
    'AE': 1.0,
    'SA': 0.95,
    'IL': 1.0,
    'TR': 0.60,  # Economic adjustment
    
    # Africa
    'ZA': 0.70,
    'NG': 0.50,
    'KE': 0.55,
}

# Tax collection settings per region
TAX_COLLECTION = {
    'EU': {
        'enabled': True,
        'vat_required': True,
        'reverse_charge': True,
    },
    'US': {
        'enabled': True,
        'sales_tax': True,
        'states': True,
    },
    'CA': {
        'enabled': True,
        'gst_hst': True,
        'provinces': True,
    },
    'AU': {
        'enabled': True,
        'gst': True,
    },
    'NZ': {
        'enabled': True,
        'gst': True,
    },
    'SG': {
        'enabled': True,
        'gst': True,
    },
    'JP': {
        'enabled': True,
        'consumption_tax': True,
    },
    'KR': {
        'enabled': True,
        'vat': True,
    },
}

def get_payment_methods_for_country(country_code: str) -> list:
    """Get supported payment methods for a country"""
    methods = ['card']  # Card is universal
    
    if country_code in REGIONAL_PAYMENT_METHODS:
        methods.extend(REGIONAL_PAYMENT_METHODS[country_code])
    
    return methods

def get_price_for_country(tier: str, country_code: str, base_price_usd: float) -> float:
    """Get adjusted price for a country"""
    adjustment = REGIONAL_PRICING_ADJUSTMENTS.get(country_code, 1.0)
    return round(base_price_usd * adjustment, 2)

def get_currency_for_country(country_code: str) -> str:
    """Get primary currency for a country"""
    for currency, countries in CURRENCY_COUNTRY_MAP.items():
        if country_code in countries:
            return currency
    return 'USD'  # Default to USD

def is_tax_collection_required(country_code: str) -> bool:
    """Check if tax collection is required for a country"""
    # Check if country is in EU
    eu_countries = CURRENCY_COUNTRY_MAP.get('EUR', [])
    if country_code in eu_countries:
        return TAX_COLLECTION.get('EU', {}).get('enabled', False)
    
    # Check other regions
    for region, config in TAX_COLLECTION.items():
        if country_code in CURRENCY_COUNTRY_MAP.get(region, []):
            return config.get('enabled', False)
    
    return False

def get_regional_disclaimer(country_code: str) -> str:
    """Get regional regulatory disclaimer"""
    disclaimers = {
        'US': "🇺🇸 This is not investment advice. Past performance does not guarantee future results.",
        'EU': "🇪🇺 Trading involves risk. 74% of retail CFD accounts lose money.",
        'GB': "🇬🇧 This service is not regulated by the FCA. Trading involves significant risk.",
        'AU': "🇦🇺 Trading involves substantial risk. Not suitable for all investors.",
        'CA': "🇨🇦 Trading involves risk. Consult a financial advisor before trading.",
        'JP': "🇯🇵 取引にはリスクが伴います。すべての投資家に適しているわけではありません。",
        'CN': "🇨🇳 交易涉及重大风险，不适合所有投资者。",
        'IN': "🇮🇳 Trading involves substantial risk. Not suitable for all investors.",
        'BR': "🇧🇷 Trading envolve risco substancial. Não é adequado para todos os investidores.",
        'MX': "🇲🇽 El trading implica un riesgo sustancial. No es adecuado para todos los inversores.",
    }
    
    # Check EU countries
    eu_countries = CURRENCY_COUNTRY_MAP.get('EUR', [])
    if country_code in eu_countries:
        return disclaimers.get('EU', disclaimers.get('US', ''))
    
    return disclaimers.get(country_code, disclaimers.get('US', ''))

# Example usage
if __name__ == "__main__":
    print("Stripe International Configuration")
    print("=" * 50)
    print(f"Supported countries: {len(STRIPE_SUPPORTED_COUNTRIES)}")
    print(f"\nExample - Netherlands:")
    print(f"  Payment methods: {get_payment_methods_for_country('NL')}")
    print(f"  Currency: {get_currency_for_country('NL')}")
    print(f"  Price adjustment: {REGIONAL_PRICING_ADJUSTMENTS.get('NL', 1.0)}")
    print(f"\nExample - Brazil:")
    print(f"  Payment methods: {get_payment_methods_for_country('BR')}")
    print(f"  Currency: {get_currency_for_country('BR')}")
    print(f"  Price adjustment: {REGIONAL_PRICING_ADJUSTMENTS.get('BR', 1.0)}")
    print(f"  Premium price: ${get_price_for_country('premium', 'BR', 39.00)}")
