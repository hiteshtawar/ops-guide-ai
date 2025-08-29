"""
HTTP request parsing functionality
"""
import json
import uuid
from typing import Dict, Any, Optional
from datetime import datetime


class RequestParser:
    """Handles HTTP request parsing and data extraction"""
    
    def parse_http_request(self, headers: Dict[str, str], body: str) -> Dict[str, Any]:
        """Parse HTTP request into structured data"""
        
        # Extract headers
        user_id = headers.get('X-User-ID', 'unknown')
        auth_header = headers.get('Authorization', '')
        content_type = headers.get('Content-Type', '')
        
        # Parse JSON body
        try:
            request_data = json.loads(body) if body else {}
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in request body: {e}")
        
        # Extract query and context
        query = request_data.get('query', '')
        context = request_data.get('context', {})
        environment = request_data.get('environment', 'dev')
        
        return {
            'user_id': user_id,
            'auth_header': auth_header,
            'content_type': content_type,
            'query': query,
            'context': context,
            'environment': environment,
            'request_data': request_data
        }
    
    def generate_request_id(self) -> str:
        """Generate unique request ID"""
        return str(uuid.uuid4())
    
    def extract_content_length(self, headers: Dict[str, str]) -> int:
        """Extract content length from headers"""
        try:
            return int(headers.get('Content-Length', 0))
        except (ValueError, TypeError):
            return 0
