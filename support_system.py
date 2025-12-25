"""
Support Ticket System
Handles user support requests and tickets
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum

class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class SupportTicketSystem:
    """Manages user support tickets"""
    
    def __init__(self, data_file: str = "support_tickets.json"):
        self.data_file = data_file
        self.tickets = {}
        self.load_data()
    
    def load_data(self):
        """Load tickets from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.tickets = json.load(f)
            except:
                self.tickets = {}
        else:
            self.tickets = {}
    
    def save_data(self):
        """Save tickets to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.tickets, f, indent=2)
    
    def create_ticket(self, user_id: int, subject: str, message: str, 
                     priority: TicketPriority = TicketPriority.MEDIUM,
                     category: str = "general") -> int:
        """Create a new support ticket"""
        ticket_id = len(self.tickets) + 1
        
        ticket = {
            'id': ticket_id,
            'user_id': user_id,
            'subject': subject,
            'message': message,
            'category': category,
            'priority': priority.value,
            'status': TicketStatus.OPEN.value,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'replies': [],
            'assigned_to': None,
            'resolved_at': None
        }
        
        self.tickets[str(ticket_id)] = ticket
        self.save_data()
        
        return ticket_id
    
    def get_ticket(self, ticket_id: int) -> Optional[Dict]:
        """Get ticket by ID"""
        return self.tickets.get(str(ticket_id))
    
    def get_user_tickets(self, user_id: int, status: Optional[TicketStatus] = None) -> List[Dict]:
        """Get all tickets for a user"""
        user_tickets = [
            ticket for ticket in self.tickets.values()
            if ticket['user_id'] == user_id
        ]
        
        if status:
            user_tickets = [
                t for t in user_tickets
                if t['status'] == status.value
            ]
        
        return sorted(user_tickets, key=lambda x: x['created_at'], reverse=True)
    
    def update_ticket_status(self, ticket_id: int, status: TicketStatus, 
                            admin_id: Optional[int] = None) -> bool:
        """Update ticket status"""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return False
        
        ticket['status'] = status.value
        ticket['updated_at'] = datetime.now().isoformat()
        
        if status == TicketStatus.RESOLVED:
            ticket['resolved_at'] = datetime.now().isoformat()
        
        if admin_id:
            ticket['assigned_to'] = admin_id
        
        self.save_data()
        return True
    
    def add_reply(self, ticket_id: int, user_id: int, message: str, 
                  is_admin: bool = False) -> bool:
        """Add a reply to a ticket"""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return False
        
        reply = {
            'user_id': user_id,
            'message': message,
            'is_admin': is_admin,
            'timestamp': datetime.now().isoformat()
        }
        
        ticket['replies'].append(reply)
        ticket['updated_at'] = datetime.now().isoformat()
        
        # Auto-update status if admin replies
        if is_admin and ticket['status'] == TicketStatus.OPEN.value:
            ticket['status'] = TicketStatus.IN_PROGRESS.value
        
        self.save_data()
        return True
    
    def get_all_tickets(self, status: Optional[TicketStatus] = None,
                       priority: Optional[TicketPriority] = None) -> List[Dict]:
        """Get all tickets (admin function)"""
        all_tickets = list(self.tickets.values())
        
        if status:
            all_tickets = [t for t in all_tickets if t['status'] == status.value]
        
        if priority:
            all_tickets = [t for t in all_tickets if t['priority'] == priority.value]
        
        return sorted(all_tickets, key=lambda x: x['created_at'], reverse=True)
    
    def get_ticket_stats(self) -> Dict:
        """Get ticket statistics"""
        all_tickets = list(self.tickets.values())
        
        return {
            'total': len(all_tickets),
            'open': len([t for t in all_tickets if t['status'] == TicketStatus.OPEN.value]),
            'in_progress': len([t for t in all_tickets if t['status'] == TicketStatus.IN_PROGRESS.value]),
            'resolved': len([t for t in all_tickets if t['status'] == TicketStatus.RESOLVED.value]),
            'closed': len([t for t in all_tickets if t['status'] == TicketStatus.CLOSED.value]),
            'urgent': len([t for t in all_tickets if t['priority'] == TicketPriority.URGENT.value]),
            'avg_response_time': self._calculate_avg_response_time()
        }
    
    def _calculate_avg_response_time(self) -> Optional[float]:
        """Calculate average response time in hours"""
        resolved_tickets = [
            t for t in self.tickets.values()
            if t['status'] == TicketStatus.RESOLVED.value and t.get('resolved_at')
        ]
        
        if not resolved_tickets:
            return None
        
        response_times = []
        for ticket in resolved_tickets:
            created = datetime.fromisoformat(ticket['created_at'])
            resolved = datetime.fromisoformat(ticket['resolved_at'])
            response_times.append((resolved - created).total_seconds() / 3600)
        
        return sum(response_times) / len(response_times) if response_times else None


def format_ticket_message(ticket: Dict) -> str:
    """Format ticket for Telegram message"""
    status_emoji = {
        'open': '🟢',
        'in_progress': '🟡',
        'resolved': '✅',
        'closed': '⚫'
    }
    
    priority_emoji = {
        'low': '🔵',
        'medium': '🟡',
        'high': '🟠',
        'urgent': '🔴'
    }
    
    emoji = status_emoji.get(ticket['status'], '⚪')
    priority_emoji_icon = priority_emoji.get(ticket['priority'], '⚪')
    
    message = f"{emoji} <b>Ticket #{ticket['id']}</b> - {ticket['subject']}\n"
    message += f"{priority_emoji_icon} Priority: {ticket['priority'].upper()}\n"
    message += f"📅 Created: {ticket['created_at'][:10]}\n"
    message += f"📝 Status: {ticket['status'].upper().replace('_', ' ')}\n"
    message += f"\n{ticket['message']}\n"
    
    if ticket['replies']:
        message += f"\n💬 Replies: {len(ticket['replies'])}"
    
    return message

