"""
Broker Partnerships Module
Manages partnerships with MT5 brokers, OANDA, Interactive Brokers, etc.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class BrokerPartnershipManager:
    """Manages broker partnerships and integrations"""
    
    def __init__(self):
        self.partnerships_file = "broker_partnerships.json"
        self.partnerships = self._load_partnerships()
    
    def _load_partnerships(self) -> Dict:
        """Load broker partnerships data"""
        try:
            with open(self.partnerships_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "partners": [],
                "target_brokers": [
                    {
                        "name": "MetaTrader 5 Brokers",
                        "type": "platform",
                        "status": "target",
                        "integration_type": "api",
                        "revenue_share": 0.20,
                        "regions": ["global"]
                    },
                    {
                        "name": "OANDA",
                        "type": "forex_focused",
                        "status": "target",
                        "integration_type": "api",
                        "revenue_share": 0.20,
                        "regions": ["US", "UK", "AU", "SG", "JP"]
                    },
                    {
                        "name": "Interactive Brokers",
                        "type": "professional",
                        "status": "target",
                        "integration_type": "api",
                        "revenue_share": 0.15,
                        "regions": ["US", "EU", "APAC"]
                    },
                    {
                        "name": "Binance",
                        "type": "crypto",
                        "status": "target",
                        "integration_type": "api",
                        "revenue_share": 0.25,
                        "regions": ["global"]
                    }
                ],
                "partnership_benefits": {
                    "revenue_share": "20% of commissions",
                    "co_marketing": True,
                    "api_integrations": True,
                    "white_label": True
                }
            }
    
    def _save_partnerships(self):
        """Save partnerships data"""
        with open(self.partnerships_file, 'w') as f:
            json.dump(self.partnerships, f, indent=2)
    
    def add_partnership(self, broker_name: str, partnership_type: str,
                       revenue_share: float, regions: List[str],
                       integration_details: Dict) -> Dict:
        """Add a new broker partnership"""
        partnership = {
            "id": len(self.partnerships["partners"]) + 1,
            "broker_name": broker_name,
            "partnership_type": partnership_type,
            "revenue_share": revenue_share,
            "regions": regions,
            "integration_details": integration_details,
            "status": "active",
            "start_date": datetime.now().isoformat(),
            "monthly_revenue": 0.0,
            "users_referred": 0
        }
        
        self.partnerships["partners"].append(partnership)
        self._save_partnerships()
        
        logger.info(f"Added partnership with {broker_name}")
        return partnership
    
    def get_partnerships_by_region(self, region: str) -> List[Dict]:
        """Get partnerships for a specific region"""
        return [
            p for p in self.partnerships["partners"]
            if region in p.get("regions", []) and p["status"] == "active"
        ]
    
    def update_partnership_revenue(self, partnership_id: int, revenue: float):
        """Update partnership revenue"""
        for partnership in self.partnerships["partners"]:
            if partnership["id"] == partnership_id:
                partnership["monthly_revenue"] = revenue
                partnership["last_updated"] = datetime.now().isoformat()
                self._save_partnerships()
                return
        
        logger.warning(f"Partnership {partnership_id} not found")
    
    def get_partnership_stats(self) -> Dict:
        """Get overall partnership statistics"""
        active_partnerships = [
            p for p in self.partnerships["partners"] 
            if p["status"] == "active"
        ]
        
        total_revenue = sum(p.get("monthly_revenue", 0) for p in active_partnerships)
        total_users = sum(p.get("users_referred", 0) for p in active_partnerships)
        
        return {
            "total_partnerships": len(active_partnerships),
            "total_monthly_revenue": total_revenue,
            "total_users_referred": total_users,
            "average_revenue_share": sum(p.get("revenue_share", 0) for p in active_partnerships) / len(active_partnerships) if active_partnerships else 0,
            "partnerships_by_type": self._group_by_type(active_partnerships)
        }
    
    def _group_by_type(self, partnerships: List[Dict]) -> Dict:
        """Group partnerships by type"""
        grouped = {}
        for p in partnerships:
            p_type = p.get("partnership_type", "unknown")
            if p_type not in grouped:
                grouped[p_type] = []
            grouped[p_type].append(p)
        return grouped

# Global instance
broker_partnership_manager = BrokerPartnershipManager()

if __name__ == "__main__":
    stats = broker_partnership_manager.get_partnership_stats()
    print("Broker Partnership Statistics:")
    print(json.dumps(stats, indent=2))



