"""
KYC/AML Verification Module for UR Trading Expert
Implements basic Know Your Customer and Anti-Money Laundering procedures
"""

import os
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict

@dataclass
class UserVerification:
    """User verification data structure"""
    telegram_id: int
    email: Optional[str] = None
    email_verified: bool = False
    email_verification_code: Optional[str] = None
    email_verification_expiry: Optional[str] = None
    name: Optional[str] = None
    location: Optional[str] = None
    verification_status: str = "pending"  # pending, verified, rejected, suspended
    verification_date: Optional[str] = None
    risk_level: str = "low"  # low, medium, high
    suspicious_activity_flags: List[str] = None
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.suspicious_activity_flags is None:
            self.suspicious_activity_flags = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()


class KYCVerificationManager:
    """Manages KYC/AML verification for users"""
    
    def __init__(self, data_file: str = "kyc_verifications.json"):
        self.data_file = data_file
        self.verifications: Dict[int, UserVerification] = {}
        self.load_data()
    
    def load_data(self):
        """Load verification data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for user_id_str, user_data in data.items():
                        user_id = int(user_id_str)
                        self.verifications[user_id] = UserVerification(**user_data)
            except Exception as e:
                print(f"[KYC] Error loading data: {e}")
                self.verifications = {}
    
    def save_data(self):
        """Save verification data to file"""
        try:
            data = {
                str(user_id): asdict(verification)
                for user_id, verification in self.verifications.items()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[KYC] Error saving data: {e}")
    
    def get_user_verification(self, telegram_id: int) -> UserVerification:
        """Get user verification record, create if doesn't exist"""
        if telegram_id not in self.verifications:
            self.verifications[telegram_id] = UserVerification(telegram_id=telegram_id)
            self.save_data()
        return self.verifications[telegram_id]
    
    def generate_verification_code(self, telegram_id: int) -> str:
        """Generate email verification code"""
        verification = self.get_user_verification(telegram_id)
        
        # Generate 6-digit code
        code = str(hashlib.sha256(
            f"{telegram_id}{time.time()}{os.urandom(16)}".encode()
        ).hexdigest()[:6].upper())
        
        verification.email_verification_code = code
        verification.email_verification_expiry = (
            datetime.now() + timedelta(hours=24)
        ).isoformat()
        verification.updated_at = datetime.now().isoformat()
        
        self.save_data()
        return code
    
    def verify_email_code(self, telegram_id: int, code: str) -> bool:
        """Verify email verification code"""
        verification = self.get_user_verification(telegram_id)
        
        if not verification.email_verification_code:
            return False
        
        if verification.email_verification_expiry:
            expiry = datetime.fromisoformat(verification.email_verification_expiry)
            if datetime.now() > expiry:
                return False
        
        if verification.email_verification_code.upper() == code.upper():
            verification.email_verified = True
            verification.email_verification_code = None
            verification.email_verification_expiry = None
            verification.verification_status = "verified"
            verification.verification_date = datetime.now().isoformat()
            verification.updated_at = datetime.now().isoformat()
            self.save_data()
            return True
        
        return False
    
    def set_user_email(self, telegram_id: int, email: str):
        """Set user email address"""
        verification = self.get_user_verification(telegram_id)
        verification.email = email.lower().strip()
        verification.updated_at = datetime.now().isoformat()
        self.save_data()
    
    def set_user_info(self, telegram_id: int, name: Optional[str] = None, 
                     location: Optional[str] = None):
        """Set user name and location"""
        verification = self.get_user_verification(telegram_id)
        if name:
            verification.name = name
        if location:
            verification.location = location
        verification.updated_at = datetime.now().isoformat()
        self.save_data()
    
    def is_email_verified(self, telegram_id: int) -> bool:
        """Check if user email is verified"""
        verification = self.get_user_verification(telegram_id)
        return verification.email_verified
    
    def is_verified(self, telegram_id: int) -> bool:
        """Check if user is fully verified"""
        verification = self.get_user_verification(telegram_id)
        return verification.verification_status == "verified"
    
    def requires_verification(self, telegram_id: int, tier: str) -> bool:
        """Check if user requires verification for tier"""
        # Free tier: no verification required
        if tier == "free":
            return False
        
        # Premium/VIP: email verification required
        return not self.is_email_verified(telegram_id)
    
    def check_suspicious_activity(self, telegram_id: int, 
                                 transaction_amount: Optional[float] = None,
                                 transaction_count: Optional[int] = None) -> List[str]:
        """Check for suspicious activity patterns"""
        flags = []
        verification = self.get_user_verification(telegram_id)
        
        # Large transaction amount (over $10,000)
        if transaction_amount and transaction_amount > 10000:
            flags.append("large_transaction")
            verification.risk_level = "high"
        
        # Multiple rapid transactions
        if transaction_count and transaction_count > 10:
            flags.append("rapid_transactions")
            if verification.risk_level == "low":
                verification.risk_level = "medium"
        
        # No email verification for premium subscription
        if not verification.email_verified and verification.verification_status == "pending":
            flags.append("unverified_premium")
        
        # Update flags
        for flag in flags:
            if flag not in verification.suspicious_activity_flags:
                verification.suspicious_activity_flags.append(flag)
        
        verification.updated_at = datetime.now().isoformat()
        self.save_data()
        
        return flags
    
    def get_verification_status(self, telegram_id: int) -> Dict:
        """Get user verification status"""
        verification = self.get_user_verification(telegram_id)
        return {
            'email_verified': verification.email_verified,
            'email': verification.email if verification.email_verified else None,
            'verification_status': verification.verification_status,
            'risk_level': verification.risk_level,
            'has_suspicious_flags': len(verification.suspicious_activity_flags) > 0,
            'name': verification.name,
            'location': verification.location
        }


# Global instance
kyc_manager = KYCVerificationManager()


def send_verification_email(email: str, code: str) -> bool:
    """Send verification email (placeholder - implement with actual email service)"""
    # TODO: Implement actual email sending
    # For now, this is a placeholder
    # In production, use services like:
    # - SendGrid
    # - AWS SES
    # - Mailgun
    # - SMTP
    
    print(f"[KYC] Verification code for {email}: {code}")
    print(f"[KYC] TODO: Implement actual email sending")
    return True


def format_verification_message(code: str) -> str:
    """Format verification code message"""
    msg = "📧 **EMAIL VERIFICATION**\n\n"
    msg += f"Your verification code is: `{code}`\n\n"
    msg += "This code expires in 24 hours.\n"
    msg += "Use `/verify [code]` to verify your email.\n\n"
    msg += "⚠️ Keep this code secure and don't share it with anyone."
    return msg

