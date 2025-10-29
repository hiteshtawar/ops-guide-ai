#!/usr/bin/env python3
"""
OpsGuide MVP Server
Simple HTTP server demonstrating request parsing, validation, and pattern-based classification
"""
import json
import sys
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add modules to path
sys.path.append(os.path.dirname(__file__))

from models import OperationalRequest, TaskId
from parsingAndValidation import RequestParser, RequestValidator
from requestClassification import PatternClassifier


class OpsGuideMVPHandler(BaseHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        # Initialize components
        self.parser = RequestParser()
        self.validator = RequestValidator()
        self.classifier = PatternClassifier()
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests"""
        
        if self.path == '/v1/request':
            self.handle_operational_request()
        else:
            self.send_error_response(404, "Endpoint not found")
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        
        if self.path == '/health':
            self.handle_health_check()
        elif self.path == '/':
            self.handle_root()
        else:
            self.send_error_response(404, "Endpoint not found")
    
    def _set_cors_headers(self):
        """Set CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-User-ID, X-Idempotency-Key, Authorization')
        self.send_header('Access-Control-Max-Age', '3600')
    
    def handle_root(self):
        """Handle GET / - show API info"""
        response_data = {
            "service": "OpsGuide MVP",
            "version": "1.0.0",
            "description": "Minimal operational request processing with pattern matching",
            "endpoints": {
                "POST /v1/request": "Submit operational request",
                "GET /health": "Health check"
            },
            "supported_tasks": [
                "CANCEL_ORDER: cancel order ORDER-123",
                "CANCEL_CASE: cancel case CASE-123",
                "CHANGE_ORDER_STATUS: change order status to completed"
            ],
            "architecture": [
                "1. HTTP Parsing & Validation",
                "2. Pattern-based Classification", 
                "3. Entity Extraction",
                "4. Structured Response"
            ]
        }
        self.send_json_response(200, response_data)
    
    def handle_health_check(self):
        """Handle GET /health"""
        response_data = {
            "status": "healthy",
            "service": "opsguide-mvp",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "1.0.0",
            "components": {
                "parsing_validation": "active",
                "pattern_classification": "active",
                "entity_extraction": "active"
            }
        }
        self.send_json_response(200, response_data)
    
    def handle_operational_request(self):
        """Handle POST /v1/request"""
        
        try:
            # Step 1: Parse HTTP request
            content_length = self.parser.extract_content_length(dict(self.headers))
            body = self.rfile.read(content_length).decode('utf-8')
            
            parsed_data = self.parser.parse_http_request(dict(self.headers), body)
            
            # Step 2: Validate request
            valid, error_message = self.validator.validate_request(
                dict(self.headers), 
                parsed_data['request_data']
            )
            
            if not valid:
                self.send_error_response(400, error_message)
                return
            
            # Step 3: Create operational request object
            request_id = self.parser.generate_request_id()
            
            operational_request = OperationalRequest(
                request_id=request_id,
                user_id=parsed_data['user_id'],
                query=parsed_data['query'],
                context=parsed_data['context'],
                environment=parsed_data['environment']
            )
            
            # Step 4: Classify request using pattern matching
            classification = self.classifier.classify(operational_request)
            
            # Step 5: Build response
            response_data = {
                "request_id": request_id,
                "status": "processed",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "input": {
                    "query": parsed_data['query'],
                    "environment": parsed_data['environment'],
                    "user_id": parsed_data['user_id']
                },
                "classification": {
                    "use_case": classification.use_case.value,
                    "task_id": classification.task_id.value if classification.task_id else None,
                    "confidence": classification.confidence,
                    "service": classification.service,
                    "environment": classification.environment
                },
                "extracted_entities": classification.extracted_entities,
                "next_steps": self._get_next_steps(classification.task_id) if classification.task_id else None
            }
            
            self.send_json_response(200, response_data)
            
        except Exception as e:
            self.send_error_response(500, f"Internal server error: {str(e)}")
    
    def _get_next_steps(self, task_id: TaskId) -> dict:
        """Get next steps based on classified task"""
        if task_id == TaskId.CANCEL_ORDER:
            return {
                "description": "Order cancellation request identified",
                "runbook": "knowledge/runbooks/cancel-order-runbook.md",
                "api_spec": "knowledge/api-specs/order-management-api.md",
                "typical_steps": [
                    "Validate order exists and is cancellable",
                    "Check user permissions",
                    "Execute cancellation via API",
                    "Verify cancellation completed"
                ]
            }
        elif task_id == TaskId.CANCEL_CASE:
            return {
                "description": "Case cancellation request identified",
                "runbook": "knowledge/runbooks/cancel-case-runbook.md",
                "api_spec": "knowledge/api-specs/order-management-api.md",
                "typical_steps": [
                    "Validate case exists and is cancellable",
                    "Check user permissions",
                    "Execute cancellation via API",
                    "Verify cancellation completed"
                ]
            }
        elif task_id == TaskId.CHANGE_ORDER_STATUS:
            return {
                "description": "Order status change request identified",
                "runbook": "knowledge/runbooks/change-order-status-runbook.md",
                "api_spec": "knowledge/api-specs/order-management-api.md",
                "typical_steps": [
                    "Validate order exists",
                    "Check status transition is valid",
                    "Update order status via API",
                    "Verify status change completed"
                ]
            }
        return None
    
    def send_json_response(self, status_code: int, data: dict):
        """Send JSON response with CORS headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self._set_cors_headers()
        self.end_headers()
        
        response_json = json.dumps(data, indent=2, default=str)
        self.wfile.write(response_json.encode('utf-8'))
    
    def send_error_response(self, status_code: int, message: str):
        """Send error response"""
        error_data = {
            "error": message,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        self.send_json_response(status_code, error_data)


def run_server(port=8093):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, OpsGuideMVPHandler)
    
    print(f"🚀 OpsGuide MVP Server starting on port {port}")
    print(f"📍 Health check: http://localhost:{port}/health")
    print(f"📍 API info: http://localhost:{port}/")
    print(f"📍 Submit request: POST http://localhost:{port}/v1/request")
    print("\n🔧 Architecture:")
    print("   1. HTTP Parsing & Validation")
    print("   2. Pattern-based Classification")
    print("   3. Entity Extraction")
    print("   4. Structured Response")
    print("\n✅ Supported Tasks:")
    print("   • CANCEL_ORDER: 'cancel order ORDER-123'")
    print("   • CANCEL_CASE: 'cancel case CASE-123'")
    print("   • CHANGE_ORDER_STATUS: 'change order status to completed'")
    print(f"\n🌐 Server ready at http://localhost:{port}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server shutting down...")
        httpd.server_close()


if __name__ == '__main__':
    run_server()
