"""
Request validation functionality
"""
from typing import Dict, Any, Optional, Tuple


class RequestValidator:
    """Handles request validation and security checks"""
    
    def validate_headers(self, headers: Dict[str, str]) -> Tuple[bool, Optional[str]]:
        """Validate required headers"""
        
        # Check Authorization header
        auth_header = headers.get('Authorization')
        if not auth_header:
            return False, "Missing Authorization header"
        
        if not auth_header.startswith('Bearer '):
            return False, "Invalid Authorization format. Use 'Bearer <token>'"
        
        # Check User ID header
        user_id = headers.get('X-User-ID')
        if not user_id:
            return False, "Missing X-User-ID header"
        
        return True, None
    
    def validate_content_type(self, headers: Dict[str, str]) -> Tuple[bool, Optional[str]]:
        """Validate content type"""
        content_type = headers.get('Content-Type', '')
        
        if not content_type.startswith('application/json'):
            return False, "Content-Type must be application/json"
        
        return True, None
    
    def validate_request_data(self, request_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate request data structure"""
        
        # Check required fields
        query = request_data.get('query')
        if not query or not isinstance(query, str):
            return False, "Missing or invalid 'query' field"
        
        if not query.strip():
            return False, "Query cannot be empty"
        
        # Validate environment if provided
        environment = request_data.get('environment')
        if environment and environment not in ['dev', 'staging', 'prod']:
            return False, "Environment must be one of: dev, staging, prod"
        
        return True, None
    
    def validate_request(self, headers: Dict[str, str], request_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Comprehensive request validation"""
        
        # Validate headers
        valid, error = self.validate_headers(headers)
        if not valid:
            return False, error
        
        # Validate content type
        valid, error = self.validate_content_type(headers)
        if not valid:
            return False, error
        
        # Validate request data
        valid, error = self.validate_request_data(request_data)
        if not valid:
            return False, error
        
        return True, None
