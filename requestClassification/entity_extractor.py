"""
Entity extraction from natural language queries
"""
import re
from typing import Optional


class EntityExtractor:
    """Extracts structured entities from natural language text"""
    
    def extract_order_id(self, query: str) -> Optional[str]:
        """Extract order ID from query using regex patterns"""
        patterns = [
            r'ORDER[_-](\d{4})[_-][\w-]+',  # ORDER-2024-TEST-001 -> 2024
            r'\border[_\s-]?(\d+)\b',       # order-12345 -> 12345
            r'\border[_\s-]?id[_\s-]?(\w+)\b',  # order id ABC123 -> ABC123
            r'\b([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})\b',  # UUID
            r'\b(\d{4,})\b'  # Any 4+ digit number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def extract_target_status(self, query: str) -> Optional[str]:
        """Extract target status for status change operations"""
        status_patterns = {
            'completed': [r'\bcomplete\b', r'\bfinish\b', r'\bdone\b', r'\bcompleted\b'],
            'cancelled': [r'\bcancel\b', r'\babort\b', r'\bterminate\b', r'\bcancelled\b'],
            'on_hold': [r'\bhold\b', r'\bpause\b', r'\bsuspend\b', r'\bon[_\s-]?hold\b'],
            'in_progress': [r'\bin[_\s-]?progress\b', r'\bactive\b', r'\bstart\b', r'\bstarted\b'],
            'under_review': [r'\breview\b', r'\bcheck\b', r'\bvalidate\b', r'\bunder[_\s-]?review\b'],
            'pending': [r'\bpending\b', r'\bwaiting\b', r'\bqueue\b'],
            'rejected': [r'\breject\b', r'\brejected\b', r'\bdeny\b', r'\bdenied\b']
        }
        
        query_lower = query.lower()
        for status, patterns in status_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return status
        
        return None
    
    def extract_priority(self, query: str) -> Optional[str]:
        """Extract priority level from query"""
        priority_patterns = {
            'high': [r'\bhigh\b', r'\burgent\b', r'\bcritical\b', r'\bemergency\b'],
            'medium': [r'\bmedium\b', r'\bnormal\b', r'\bstandard\b'],
            'low': [r'\blow\b', r'\bminor\b', r'\broutine\b']
        }
        
        query_lower = query.lower()
        for priority, patterns in priority_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return priority
        
        return None
