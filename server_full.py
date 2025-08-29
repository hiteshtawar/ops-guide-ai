#!/usr/bin/env python3
"""
OpsGuide Full AI Server
Complete operational intelligence with knowledge retrieval, AI plan generation, and risk assessment
"""
import json
import sys
import os
import asyncio
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add modules to path
sys.path.append(os.path.dirname(__file__))

from models import OperationalRequest, TaskId
from parsingAndValidation import RequestParser, RequestValidator
from requestClassification import PatternClassifier
from knowledgeRetrieval import VectorSearchEngine
from planGeneration import PlanGenerator
from riskAssessment import RiskEngine, PolicyValidator, ApprovalManager


class OpsGuideFullHandler(BaseHTTPRequestHandler):
    
    def __init__(self, *args, **kwargs):
        # Initialize all components
        self.parser = RequestParser()
        self.validator = RequestValidator()
        self.classifier = PatternClassifier()
        self.knowledge_engine = VectorSearchEngine()
        self.plan_generator = PlanGenerator()
        self.risk_engine = RiskEngine()
        self.policy_validator = PolicyValidator()
        self.approval_manager = ApprovalManager()
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests"""
        
        if self.path == '/v1/request':
            self.handle_full_operational_request()
        elif self.path.startswith('/v1/approve/'):
            self.handle_approval_decision()
        else:
            self.send_error_response(404, "Endpoint not found")
    
    def do_GET(self):
        """Handle GET requests"""
        
        if self.path == '/health':
            self.handle_health_check()
        elif self.path == '/':
            self.handle_root()
        elif self.path.startswith('/v1/status/'):
            self.handle_status_check()
        else:
            self.send_error_response(404, "Endpoint not found")
    
    def handle_root(self):
        """Handle GET / - show full API info"""
        response_data = {
            "service": "OpsGuide Full AI System",
            "version": "2.0.0",
            "description": "Complete operational intelligence with AI-powered plan generation",
            "endpoints": {
                "POST /v1/request": "Submit operational request for full AI processing",
                "GET /v1/status/{request_id}": "Check request status and approval",
                "POST /v1/approve/{request_id}": "Approve/reject operational request",
                "GET /health": "Health check"
            },
            "capabilities": [
                "🧠 Pattern-based Classification",
                "🔍 Vector Knowledge Retrieval (RAG)",
                "🤖 AI Plan Generation (Claude)",
                "⚖️ Risk Assessment Engine",
                "📋 Policy Validation",
                "✅ Approval Workflows"
            ],
            "architecture": [
                "1. HTTP Parsing & Validation",
                "2. Pattern-based Classification", 
                "3. Vector Knowledge Search (OpenSearch)",
                "4. AI Plan Generation (Bedrock Claude)",
                "5. Risk Assessment & Policy Validation",
                "6. Approval Workflow Management"
            ],
            "supported_tasks": [
                "CANCEL_CASE: 'cancel case CASE-123'",
                "CHANGE_CASE_STATUS: 'change case status to completed'"
            ]
        }
        self.send_json_response(200, response_data)
    
    def handle_health_check(self):
        """Handle GET /health"""
        response_data = {
            "status": "healthy",
            "service": "opsguide-full-ai",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "2.0.0",
            "components": {
                "parsing_validation": "active",
                "pattern_classification": "active",
                "knowledge_retrieval": "simulated",  # TODO: Connect to OpenSearch
                "ai_plan_generation": "simulated",   # TODO: Connect to Bedrock
                "risk_assessment": "active",
                "policy_validation": "active",
                "approval_management": "active"
            }
        }
        self.send_json_response(200, response_data)
    
    def handle_full_operational_request(self):
        """Handle POST /v1/request with complete AI pipeline"""
        
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
            
            # Process the full AI pipeline asynchronously
            result = asyncio.run(self._process_full_pipeline(operational_request))
            
            self.send_json_response(result["status_code"], result["data"])
            
        except Exception as e:
            self.send_error_response(500, f"Internal server error: {str(e)}")
    
    async def _process_full_pipeline(self, request: OperationalRequest) -> dict:
        """Process request through complete AI pipeline"""
        
        try:
            # Step 1: Classify request using pattern matching
            classification = self.classifier.classify(request)
            
            if not classification.task_id:
                return {
                    "status_code": 400,
                    "data": {
                        "error": "Could not identify operational task",
                        "classification": {
                            "confidence": classification.confidence,
                            "extracted_entities": classification.extracted_entities
                        }
                    }
                }
            
            # Step 2: Retrieve relevant knowledge using vector search
            knowledge_results = await self.knowledge_engine.search_knowledge(
                query=request.query,
                classification=classification
            )
            
            # Step 3: Generate operational plan using AI
            operational_plan = await self.plan_generator.generate_operational_plan(
                request=request,
                classification=classification,
                knowledge_results=knowledge_results
            )
            
            # Step 4: Assess risk
            risk_assessment = self.risk_engine.assess_risk(
                request=request,
                classification=classification,
                plan_data=operational_plan.__dict__
            )
            
            # Step 5: Validate against policies
            policy_validation = self.policy_validator.validate_request(
                request=request,
                classification=classification,
                risk_assessment=risk_assessment
            )
            
            if not policy_validation.allowed:
                return {
                    "status_code": 403,
                    "data": {
                        "error": "Operation violates organizational policies",
                        "violations": [
                            {
                                "policy": v.policy_name,
                                "type": v.violation_type,
                                "description": v.description,
                                "severity": v.severity
                            } for v in policy_validation.violations
                        ]
                    }
                }
            
            # Step 6: Check if approval is needed
            approval_request = None
            if risk_assessment.requires_approval:
                approval_request = self.approval_manager.create_approval_request(
                    request_id=request.request_id,
                    operation_summary=operational_plan.summary,
                    risk_level=risk_assessment.risk_level.value,
                    requester=request.user_id,
                    environment=request.environment
                )
            
            # Step 7: Build comprehensive response
            response_data = {
                "request_id": request.request_id,
                "status": "awaiting_approval" if approval_request else "ready_for_execution",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "input": {
                    "query": request.query,
                    "environment": request.environment,
                    "user_id": request.user_id
                },
                "classification": {
                    "use_case": classification.use_case.value,
                    "task_id": classification.task_id.value,
                    "confidence": classification.confidence,
                    "service": classification.service,
                    "environment": classification.environment,
                    "extracted_entities": classification.extracted_entities
                },
                "knowledge_retrieval": {
                    "sources_found": len(knowledge_results),
                    "sources": [
                        {
                            "uri": result.source_uri,
                            "relevance_score": result.score,
                            "metadata": result.metadata
                        } for result in knowledge_results
                    ]
                },
                "operational_plan": {
                    "summary": operational_plan.summary,
                    "risk_level": operational_plan.risk_level,
                    "estimated_duration": operational_plan.estimated_duration,
                    "requires_approval": operational_plan.requires_approval,
                    "pre_checks": operational_plan.pre_checks,
                    "procedure": operational_plan.procedure,
                    "post_checks": operational_plan.post_checks,
                    "rollback": operational_plan.rollback,
                    "citations": operational_plan.citations
                },
                "risk_assessment": {
                    "risk_level": risk_assessment.risk_level.value,
                    "overall_score": risk_assessment.score,
                    "requires_approval": risk_assessment.requires_approval,
                    "factors": [
                        {
                            "name": factor.name,
                            "score": factor.score,
                            "weight": factor.weight,
                            "description": factor.description
                        } for factor in risk_assessment.factors
                    ],
                    "constraints": risk_assessment.constraints
                },
                "policy_validation": {
                    "allowed": policy_validation.allowed,
                    "violations": [
                        {
                            "policy": v.policy_name,
                            "type": v.violation_type,
                            "description": v.description,
                            "severity": v.severity
                        } for v in policy_validation.violations
                    ],
                    "warnings": policy_validation.warnings
                },
                "approval": {
                    "required": approval_request is not None,
                    "request_id": approval_request.request_id if approval_request else None,
                    "status": approval_request.status.value if approval_request else None,
                    "expires_at": approval_request.expires_at.isoformat() + "Z" if approval_request else None,
                    "approvers": approval_request.approvers if approval_request else []
                } if approval_request else {"required": False}
            }
            
            return {
                "status_code": 202,  # Accepted for processing
                "data": response_data
            }
            
        except Exception as e:
            return {
                "status_code": 500,
                "data": {"error": f"Pipeline processing failed: {str(e)}"}
            }
    
    def handle_status_check(self):
        """Handle GET /v1/status/{request_id}"""
        path_parts = self.path.split('/')
        if len(path_parts) < 4:
            self.send_error_response(400, "Invalid status request")
            return
        
        request_id = path_parts[3]
        approval_request = self.approval_manager.check_approval_status(request_id)
        
        if not approval_request:
            self.send_error_response(404, "Request not found")
            return
        
        response_data = {
            "request_id": request_id,
            "status": approval_request.status.value,
            "created_at": approval_request.created_at.isoformat() + "Z",
            "expires_at": approval_request.expires_at.isoformat() + "Z",
            "operation_summary": approval_request.operation_summary,
            "risk_level": approval_request.risk_level,
            "requester": approval_request.requester,
            "approvers": approval_request.approvers,
            "approved_by": approval_request.approved_by,
            "approved_at": approval_request.approved_at.isoformat() + "Z" if approval_request.approved_at else None,
            "rejection_reason": approval_request.rejection_reason
        }
        
        self.send_json_response(200, response_data)
    
    def handle_approval_decision(self):
        """Handle POST /v1/approve/{request_id}"""
        # TODO: Implement approval decision handling
        self.send_error_response(501, "Approval decisions not yet implemented")
    
    def send_json_response(self, status_code: int, data: dict):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
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


def run_full_server(port=8094):
    """Run the full AI HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, OpsGuideFullHandler)
    
    print(f"🚀 OpsGuide Full AI Server starting on port {port}")
    print(f"📍 Health check: http://localhost:{port}/health")
    print(f"📍 API info: http://localhost:{port}/")
    print(f"📍 Submit request: POST http://localhost:{port}/v1/request")
    print("\n🧠 Full AI Architecture:")
    print("   1. HTTP Parsing & Validation")
    print("   2. Pattern-based Classification")
    print("   3. Vector Knowledge Search (OpenSearch)")
    print("   4. AI Plan Generation (Bedrock Claude)")
    print("   5. Risk Assessment & Policy Validation")
    print("   6. Approval Workflow Management")
    print("\n🎯 Capabilities:")
    print("   • 🔍 RAG Knowledge Retrieval")
    print("   • 🤖 AI-Powered Plan Generation")
    print("   • ⚖️ Risk Assessment Engine")
    print("   • 📋 Policy Validation")
    print("   • ✅ Approval Workflows")
    print(f"\n🌐 Full AI Server ready at http://localhost:{port}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server shutting down...")
        httpd.server_close()


if __name__ == '__main__':
    run_full_server()
