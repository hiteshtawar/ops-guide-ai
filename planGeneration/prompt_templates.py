"""
Prompt Templates for different operational tasks
"""
from typing import Dict, Any
from models import OperationalRequest, ClassificationResult, TaskId


class PromptTemplateManager:
    """Manages prompt templates for different operational tasks"""
    
    def __init__(self):
        self.templates = {
            TaskId.CANCEL_CASE: self._get_cancel_case_template(),
            TaskId.CHANGE_CASE_STATUS: self._get_change_status_template(),
            TaskId.RECONCILE_CASE_DATA: self._get_reconcile_data_template()
        }
    
    def build_prompt(
        self,
        request: OperationalRequest,
        classification: ClassificationResult,
        context: str,
        constraints: Dict[str, Any]
    ) -> str:
        """
        Build complete prompt for Claude based on task type
        
        TODO: Implement dynamic prompt building:
        1. Select appropriate template
        2. Inject context and constraints
        3. Add environment-specific guidance
        4. Include safety and validation instructions
        """
        
        template = self.templates.get(
            classification.task_id, 
            self._get_generic_template()
        )
        
        return template.format(
            user_id=request.user_id,
            query=request.query,
            task_id=classification.task_id.value if classification.task_id else "UNKNOWN",
            environment=request.environment,
            service=classification.service or "Unknown",
            case_id=classification.extracted_entities.get("case_id", "Unknown"),
            target_status=classification.extracted_entities.get("target_status", "N/A"),
            context=context,
            api_only=constraints.get("api_only", True),
            approval_required=constraints.get("approval_required", True),
            max_risk_level=constraints.get("max_risk_level", "MEDIUM"),
            rollback_window=constraints.get("rollback_window_hours", 24)
        )
    
    def _get_cancel_case_template(self) -> str:
        """Template for case cancellation operations"""
        return """You are OpsGuide, an expert operational assistant that provides safe, step-by-step procedures for infrastructure and application operations.

OPERATIONAL REQUEST:
User: {user_id}
Query: "{query}"
Task Type: {task_id}
Environment: {environment}
Service: {service}
Case ID: {case_id}

POLICY CONSTRAINTS:
- API-only operations: {api_only}
- Approval required: {approval_required}
- Environment: {environment}
- Maximum risk level: {max_risk_level}
- Rollback window: {rollback_window} hours

RETRIEVED CONTEXT:
{context}

INSTRUCTIONS:
Generate a complete operational plan for CANCELLING a case with the following structure:

1. SUMMARY: One-sentence description of the cancellation operation
2. RISK ASSESSMENT: LOW, MEDIUM, or HIGH based on environment and impact
3. PRE-CHECKS: Validations to perform before cancellation
4. PROCEDURE: Step-by-step cancellation process using ONLY APIs
5. POST-CHECKS: Verification steps after cancellation
6. ROLLBACK: How to restore the case if cancellation needs to be reversed
7. ESTIMATED DURATION: Expected time to complete

CRITICAL REQUIREMENTS:
- Use ONLY the API endpoints mentioned in the retrieved context
- Include specific API calls with endpoints, methods, and parameters
- Every step must be reversible or have a rollback path
- All recommendations must be supported by the retrieved documents
- No direct database operations - use APIs only
- Include authorization and validation checks
- Provide specific error handling guidance
- Consider business rules and dependencies

RESPONSE FORMAT:
Respond with a valid JSON object matching this exact structure:

{{
  "summary": "Brief description of the cancellation operation",
  "risk_level": "LOW|MEDIUM|HIGH",
  "requires_approval": true|false,
  "estimated_duration": "X minutes",
  "pre_checks": [
    {{
      "name": "Check name",
      "description": "What this validates",
      "api_call": "GET /api/endpoint",
      "expected_result": "Expected response",
      "required": true
    }}
  ],
  "procedure": [
    {{
      "step": 1,
      "name": "Step name",
      "description": "What this step does",
      "action": "API call or action to perform",
      "expected_result": "What should happen"
    }}
  ],
  "post_checks": [
    {{
      "name": "Verification name",
      "description": "What to verify",
      "api_call": "GET /api/endpoint",
      "expected_result": "Expected state"
    }}
  ],
  "rollback": [
    {{
      "step": 1,
      "name": "Rollback step",
      "description": "How to undo this operation",
      "action": "API call to reverse",
      "condition": "When to apply this rollback"
    }}
  ]
}}"""
    
    def _get_change_status_template(self) -> str:
        """Template for case status change operations"""
        return """You are OpsGuide, an expert operational assistant for case status management.

OPERATIONAL REQUEST:
User: {user_id}
Query: "{query}"
Task Type: {task_id}
Environment: {environment}
Service: {service}
Case ID: {case_id}
Target Status: {target_status}

POLICY CONSTRAINTS:
- API-only operations: {api_only}
- Approval required: {approval_required}
- Environment: {environment}
- Maximum risk level: {max_risk_level}

RETRIEVED CONTEXT:
{context}

INSTRUCTIONS:
Generate a complete operational plan for CHANGING CASE STATUS with proper validation and state transitions.

Focus on:
- Status transition validation
- Business rule compliance
- State consistency checks
- Audit trail maintenance

Use the same JSON response format as the cancellation template, but adapt the steps for status changes."""
    
    def _get_reconcile_data_template(self) -> str:
        """Template for data reconciliation operations"""
        return """You are OpsGuide, an expert operational assistant for data reconciliation.

OPERATIONAL REQUEST:
User: {user_id}
Query: "{query}"
Task Type: {task_id}
Environment: {environment}
Service: {service}
Case ID: {case_id}

RETRIEVED CONTEXT:
{context}

INSTRUCTIONS:
Generate a complete operational plan for DATA RECONCILIATION with focus on:
- Data consistency validation
- Conflict resolution
- Backup and recovery procedures
- Minimal disruption approach

Use the same JSON response format, adapted for reconciliation operations."""
    
    def _get_generic_template(self) -> str:
        """Generic template for unknown task types"""
        return """You are OpsGuide, an expert operational assistant.

OPERATIONAL REQUEST:
User: {user_id}
Query: "{query}"
Task Type: {task_id}
Environment: {environment}

RETRIEVED CONTEXT:
{context}

INSTRUCTIONS:
Based on the query and retrieved context, generate a safe operational plan.
Use the standard JSON response format with appropriate steps for the requested operation."""
