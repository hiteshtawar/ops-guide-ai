"""
Risk Engine - Calculates operational risk based on multiple factors
"""
from typing import Dict, Any, List
from enum import Enum
from models import OperationalRequest, ClassificationResult, TaskId


class RiskLevel(str, Enum):
    """Risk levels for operations"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskFactor:
    """Represents a risk factor with weight and score"""
    def __init__(self, name: str, score: float, weight: float, description: str):
        self.name = name
        self.score = score  # 0.0 to 1.0
        self.weight = weight  # Importance multiplier
        self.description = description


class RiskAssessment:
    """Complete risk assessment result"""
    def __init__(self, risk_level: RiskLevel, score: float, factors: List[RiskFactor], 
                 requires_approval: bool, constraints: Dict[str, Any]):
        self.risk_level = risk_level
        self.score = score
        self.factors = factors
        self.requires_approval = requires_approval
        self.constraints = constraints


class RiskEngine:
    """Calculates operational risk based on multiple factors"""
    
    def __init__(self):
        # Environment risk weights
        self.environment_risk = {
            "dev": 0.1,
            "staging": 0.3,
            "prod": 1.0
        }
        
        # Task type risk weights
        self.task_risk = {
            TaskId.CANCEL_CASE: 0.7,  # Medium-high risk
            TaskId.CHANGE_CASE_STATUS: 0.4,  # Medium risk
            TaskId.RECONCILE_CASE_DATA: 0.8  # High risk
        }
        
        # Business hours factor (lower risk during business hours)
        self.business_hours_factor = 0.8
        
        # Risk thresholds
        self.risk_thresholds = {
            RiskLevel.LOW: 0.3,
            RiskLevel.MEDIUM: 0.6,
            RiskLevel.HIGH: 0.8,
            RiskLevel.CRITICAL: 1.0
        }
    
    def assess_risk(
        self,
        request: OperationalRequest,
        classification: ClassificationResult,
        plan_data: Dict[str, Any] = None
    ) -> RiskAssessment:
        """
        Perform comprehensive risk assessment
        
        TODO: Implement advanced risk calculation:
        1. Analyze operational impact
        2. Consider historical failure rates
        3. Evaluate user permissions and experience
        4. Check system load and maintenance windows
        5. Assess data sensitivity and compliance requirements
        """
        
        risk_factors = []
        
        # Environment risk factor
        env_risk = self.environment_risk.get(request.environment, 0.5)
        risk_factors.append(RiskFactor(
            name="Environment Risk",
            score=env_risk,
            weight=2.0,
            description=f"Risk associated with {request.environment} environment"
        ))
        
        # Task type risk factor
        task_risk = self.task_risk.get(classification.task_id, 0.5)
        risk_factors.append(RiskFactor(
            name="Task Complexity",
            score=task_risk,
            weight=1.5,
            description=f"Risk associated with {classification.task_id} operation"
        ))
        
        # Time-based risk factor
        time_risk = self._calculate_time_risk()
        risk_factors.append(RiskFactor(
            name="Timing Risk",
            score=time_risk,
            weight=0.5,
            description="Risk based on current time and business hours"
        ))
        
        # User experience risk factor
        user_risk = self._calculate_user_risk(request.user_id)
        risk_factors.append(RiskFactor(
            name="User Experience",
            score=user_risk,
            weight=1.0,
            description="Risk based on user's operational experience"
        ))
        
        # Calculate overall risk score
        total_weighted_score = sum(factor.score * factor.weight for factor in risk_factors)
        total_weight = sum(factor.weight for factor in risk_factors)
        overall_score = total_weighted_score / total_weight
        
        # Determine risk level
        risk_level = self._score_to_risk_level(overall_score)
        
        # Determine approval requirements
        requires_approval = self._requires_approval(risk_level, request.environment, classification.task_id)
        
        # Build constraints
        constraints = self._build_constraints(risk_level, request.environment, classification.task_id)
        
        return RiskAssessment(
            risk_level=risk_level,
            score=overall_score,
            factors=risk_factors,
            requires_approval=requires_approval,
            constraints=constraints
        )
    
    def _calculate_time_risk(self) -> float:
        """
        Calculate risk based on current time
        
        TODO: Implement time-based risk calculation:
        1. Check if within business hours
        2. Consider maintenance windows
        3. Evaluate weekend/holiday risk
        4. Check system load patterns
        """
        from datetime import datetime
        
        now = datetime.now()
        hour = now.hour
        
        # Higher risk outside business hours (9 AM - 5 PM)
        if 9 <= hour <= 17:
            return 0.2  # Low risk during business hours
        elif 6 <= hour <= 9 or 17 <= hour <= 22:
            return 0.5  # Medium risk during extended hours
        else:
            return 0.8  # High risk during night hours
    
    def _calculate_user_risk(self, user_id: str) -> float:
        """
        Calculate risk based on user experience and permissions
        
        TODO: Implement user-based risk calculation:
        1. Check user's operational history
        2. Evaluate success/failure rates
        3. Verify current permissions
        4. Consider training and certifications
        """
        # Placeholder: assume medium risk for unknown users
        if "admin" in user_id.lower() or "ops" in user_id.lower():
            return 0.2  # Low risk for ops users
        elif "engineer" in user_id.lower():
            return 0.4  # Medium risk for engineers
        else:
            return 0.7  # Higher risk for unknown users
    
    def _score_to_risk_level(self, score: float) -> RiskLevel:
        """Convert numeric score to risk level"""
        if score <= self.risk_thresholds[RiskLevel.LOW]:
            return RiskLevel.LOW
        elif score <= self.risk_thresholds[RiskLevel.MEDIUM]:
            return RiskLevel.MEDIUM
        elif score <= self.risk_thresholds[RiskLevel.HIGH]:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _requires_approval(self, risk_level: RiskLevel, environment: str, task_id: TaskId) -> bool:
        """
        Determine if operation requires approval
        
        TODO: Implement policy-based approval logic:
        1. Check organizational policies
        2. Consider compliance requirements
        3. Evaluate delegation rules
        4. Check emergency procedures
        """
        # Production always requires approval for medium+ risk
        if environment == "prod" and risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return True
        
        # High and critical risk always require approval
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return True
        
        # Specific task requirements
        if task_id == TaskId.CANCEL_CASE and environment in ["staging", "prod"]:
            return True
        
        return False
    
    def _build_constraints(self, risk_level: RiskLevel, environment: str, task_id: TaskId) -> Dict[str, Any]:
        """
        Build operational constraints based on risk assessment
        
        TODO: Implement comprehensive constraint building:
        1. Set execution timeouts
        2. Define rollback requirements
        3. Specify monitoring needs
        4. Add notification requirements
        """
        constraints = {
            "api_only": True,  # Always use APIs, never direct DB access
            "max_retries": 3,
            "timeout_minutes": 30,
            "rollback_required": risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL],
            "monitoring_required": risk_level != RiskLevel.LOW,
            "notification_required": risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        }
        
        # Environment-specific constraints
        if environment == "prod":
            constraints.update({
                "max_retries": 1,  # Be more careful in prod
                "timeout_minutes": 15,  # Shorter timeout in prod
                "backup_required": True,
                "approval_timeout_hours": 24
            })
        
        # Task-specific constraints
        if task_id == TaskId.CANCEL_CASE:
            constraints.update({
                "confirmation_required": True,
                "audit_trail_required": True
            })
        
        return constraints
