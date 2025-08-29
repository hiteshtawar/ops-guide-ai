"""
Policy Validator - Validates operations against organizational policies
"""
from typing import Dict, Any, List, Optional
from models import OperationalRequest, ClassificationResult
from planGeneration.plan_generator import OperationalPlan


class PolicyViolation:
    """Represents a policy violation"""
    def __init__(self, policy_name: str, violation_type: str, description: str, severity: str):
        self.policy_name = policy_name
        self.violation_type = violation_type
        self.description = description
        self.severity = severity  # "WARNING", "ERROR", "CRITICAL"


class PolicyValidationResult:
    """Result of policy validation"""
    def __init__(self, allowed: bool, violations: List[PolicyViolation], 
                 constraints: Dict[str, Any], warnings: List[str]):
        self.allowed = allowed
        self.violations = violations
        self.constraints = constraints
        self.warnings = warnings


class PolicyValidator:
    """Validates operations against organizational policies and compliance rules"""
    
    def __init__(self):
        # Core organizational policies
        self.policies = {
            "api_only": {
                "description": "All operations must use APIs, no direct database access",
                "enforcement": "STRICT",
                "exceptions": []
            },
            "approval_required": {
                "description": "High-risk operations require approval",
                "enforcement": "STRICT",
                "exceptions": ["emergency_procedures"]
            },
            "business_hours": {
                "description": "Non-emergency operations should occur during business hours",
                "enforcement": "WARNING",
                "exceptions": ["maintenance_windows"]
            },
            "change_management": {
                "description": "All changes must follow change management process",
                "enforcement": "STRICT",
                "exceptions": []
            }
        }
        
        # Environment-specific policies
        self.environment_policies = {
            "prod": {
                "approval_required": True,
                "max_risk_level": "MEDIUM",
                "backup_required": True,
                "rollback_plan_required": True,
                "notification_required": True
            },
            "staging": {
                "approval_required": False,
                "max_risk_level": "HIGH",
                "backup_required": False,
                "rollback_plan_required": True,
                "notification_required": False
            },
            "dev": {
                "approval_required": False,
                "max_risk_level": "HIGH",
                "backup_required": False,
                "rollback_plan_required": False,
                "notification_required": False
            }
        }
    
    def validate_request(
        self,
        request: OperationalRequest,
        classification: ClassificationResult,
        risk_assessment: Any = None
    ) -> PolicyValidationResult:
        """
        Validate operational request against policies
        
        TODO: Implement comprehensive request validation:
        1. Check user permissions and roles
        2. Validate against compliance requirements
        3. Verify change management process
        4. Check maintenance windows and blackout periods
        5. Validate business justification
        """
        violations = []
        warnings = []
        constraints = {}
        
        # Get environment policy
        env_policy = self.environment_policies.get(request.environment, self.environment_policies["prod"])
        
        # Validate environment-specific requirements
        if request.environment == "prod":
            # Production requires special handling
            if not self._has_production_access(request.user_id):
                violations.append(PolicyViolation(
                    policy_name="production_access",
                    violation_type="AUTHORIZATION",
                    description=f"User {request.user_id} does not have production access",
                    severity="ERROR"
                ))
        
        # Validate task-specific policies
        task_violations = self._validate_task_policies(classification, request)
        violations.extend(task_violations)
        
        # Check time-based policies
        time_warnings = self._validate_time_policies(request)
        warnings.extend(time_warnings)
        
        # Build constraints from policies
        constraints = self._build_policy_constraints(env_policy, classification)
        
        # Determine if operation is allowed
        allowed = len([v for v in violations if v.severity in ["ERROR", "CRITICAL"]]) == 0
        
        return PolicyValidationResult(
            allowed=allowed,
            violations=violations,
            constraints=constraints,
            warnings=warnings
        )
    
    def validate_plan(self, plan: OperationalPlan, request: OperationalRequest) -> PolicyValidationResult:
        """
        Validate generated operational plan against policies
        
        TODO: Implement plan validation:
        1. Check all API calls are authorized
        2. Verify rollback procedures exist
        3. Validate risk mitigation steps
        4. Check compliance with security policies
        5. Ensure proper audit trail
        """
        violations = []
        warnings = []
        
        # Validate API usage
        api_violations = self._validate_api_usage(plan)
        violations.extend(api_violations)
        
        # Validate rollback procedures
        if request.environment == "prod" and not plan.rollback:
            violations.append(PolicyViolation(
                policy_name="rollback_required",
                violation_type="MISSING_PROCEDURE",
                description="Production operations must include rollback procedures",
                severity="ERROR"
            ))
        
        # Validate risk level compliance
        env_policy = self.environment_policies.get(request.environment, {})
        max_risk = env_policy.get("max_risk_level", "HIGH")
        
        if self._risk_exceeds_limit(plan.risk_level, max_risk):
            violations.append(PolicyViolation(
                policy_name="max_risk_level",
                violation_type="RISK_EXCEEDED",
                description=f"Plan risk level {plan.risk_level} exceeds maximum {max_risk} for {request.environment}",
                severity="ERROR"
            ))
        
        allowed = len([v for v in violations if v.severity in ["ERROR", "CRITICAL"]]) == 0
        
        return PolicyValidationResult(
            allowed=allowed,
            violations=violations,
            constraints={},
            warnings=warnings
        )
    
    def _has_production_access(self, user_id: str) -> bool:
        """
        Check if user has production access
        
        TODO: Implement actual user permission checking:
        1. Query user management system
        2. Check role-based access control
        3. Verify current permissions
        4. Check for temporary access grants
        """
        # Placeholder: allow ops and admin users
        return any(role in user_id.lower() for role in ["ops", "admin", "engineer"])
    
    def _validate_task_policies(
        self, 
        classification: ClassificationResult, 
        request: OperationalRequest
    ) -> List[PolicyViolation]:
        """Validate task-specific policies"""
        violations = []
        
        # Case cancellation policies
        if classification.task_id and "CANCEL" in classification.task_id.value:
            if request.environment == "prod" and not request.context.get("business_justification"):
                violations.append(PolicyViolation(
                    policy_name="business_justification",
                    violation_type="MISSING_CONTEXT",
                    description="Production case cancellations require business justification",
                    severity="WARNING"
                ))
        
        return violations
    
    def _validate_time_policies(self, request: OperationalRequest) -> List[str]:
        """Validate time-based policies"""
        warnings = []
        
        from datetime import datetime
        now = datetime.now()
        hour = now.hour
        
        # Check business hours
        if request.environment == "prod" and not (9 <= hour <= 17):
            warnings.append("Production operation requested outside business hours")
        
        # Check weekend operations
        if now.weekday() >= 5:  # Saturday or Sunday
            warnings.append("Operation requested during weekend")
        
        return warnings
    
    def _validate_api_usage(self, plan: OperationalPlan) -> List[PolicyViolation]:
        """Validate that plan uses only approved APIs"""
        violations = []
        
        # TODO: Implement API validation
        # 1. Check against approved API registry
        # 2. Validate API versions and endpoints
        # 3. Check for deprecated API usage
        # 4. Verify authentication requirements
        
        return violations
    
    def _risk_exceeds_limit(self, plan_risk: str, max_risk: str) -> bool:
        """Check if plan risk exceeds environment limit"""
        risk_levels = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        return risk_levels.get(plan_risk, 4) > risk_levels.get(max_risk, 3)
    
    def _build_policy_constraints(
        self, 
        env_policy: Dict[str, Any], 
        classification: ClassificationResult
    ) -> Dict[str, Any]:
        """Build constraints from policy requirements"""
        constraints = {
            "api_only": True,
            "approval_required": env_policy.get("approval_required", False),
            "backup_required": env_policy.get("backup_required", False),
            "rollback_plan_required": env_policy.get("rollback_plan_required", False),
            "notification_required": env_policy.get("notification_required", False),
            "max_risk_level": env_policy.get("max_risk_level", "HIGH")
        }
        
        return constraints
