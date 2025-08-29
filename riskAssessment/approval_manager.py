"""
Approval Manager - Handles approval workflows for high-risk operations
"""
from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime, timedelta


class ApprovalStatus(str, Enum):
    """Approval status for operations"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class ApprovalRequest:
    """Represents an approval request"""
    def __init__(self, request_id: str, operation_summary: str, risk_level: str, 
                 requester: str, approvers: List[str], expires_at: datetime):
        self.request_id = request_id
        self.operation_summary = operation_summary
        self.risk_level = risk_level
        self.requester = requester
        self.approvers = approvers
        self.status = ApprovalStatus.PENDING
        self.created_at = datetime.utcnow()
        self.expires_at = expires_at
        self.approved_by = None
        self.approved_at = None
        self.rejection_reason = None


class ApprovalManager:
    """Manages approval workflows for operational requests"""
    
    def __init__(self):
        # Approval policies by risk level
        self.approval_policies = {
            "LOW": {
                "required": False,
                "approvers_needed": 0,
                "timeout_hours": 0
            },
            "MEDIUM": {
                "required": True,
                "approvers_needed": 1,
                "timeout_hours": 24,
                "eligible_approvers": ["ops_lead", "senior_engineer"]
            },
            "HIGH": {
                "required": True,
                "approvers_needed": 2,
                "timeout_hours": 12,
                "eligible_approvers": ["ops_manager", "engineering_manager"]
            },
            "CRITICAL": {
                "required": True,
                "approvers_needed": 2,
                "timeout_hours": 4,
                "eligible_approvers": ["ops_director", "cto", "vp_engineering"]
            }
        }
        
        # In-memory storage for demo (TODO: use persistent storage)
        self.approval_requests = {}
    
    def create_approval_request(
        self,
        request_id: str,
        operation_summary: str,
        risk_level: str,
        requester: str,
        environment: str
    ) -> Optional[ApprovalRequest]:
        """
        Create approval request for high-risk operations
        
        TODO: Implement comprehensive approval workflow:
        1. Determine required approvers based on operation type
        2. Send notifications to approvers
        3. Set up approval timeouts
        4. Integrate with approval systems (Slack, email, etc.)
        5. Handle escalation procedures
        """
        
        policy = self.approval_policies.get(risk_level, self.approval_policies["HIGH"])
        
        if not policy["required"]:
            return None  # No approval needed
        
        # Determine eligible approvers
        eligible_approvers = self._get_eligible_approvers(risk_level, environment)
        
        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(hours=policy["timeout_hours"])
        
        # Create approval request
        approval_request = ApprovalRequest(
            request_id=request_id,
            operation_summary=operation_summary,
            risk_level=risk_level,
            requester=requester,
            approvers=eligible_approvers,
            expires_at=expires_at
        )
        
        # Store request
        self.approval_requests[request_id] = approval_request
        
        # TODO: Send notifications to approvers
        self._notify_approvers(approval_request)
        
        return approval_request
    
    def check_approval_status(self, request_id: str) -> Optional[ApprovalRequest]:
        """
        Check current approval status
        
        TODO: Implement status checking:
        1. Check for timeouts
        2. Update status based on responses
        3. Handle partial approvals
        4. Check for policy changes
        """
        approval_request = self.approval_requests.get(request_id)
        
        if not approval_request:
            return None
        
        # Check for expiration
        if datetime.utcnow() > approval_request.expires_at and approval_request.status == ApprovalStatus.PENDING:
            approval_request.status = ApprovalStatus.EXPIRED
        
        return approval_request
    
    def approve_request(self, request_id: str, approver: str, comments: str = "") -> bool:
        """
        Approve an operational request
        
        TODO: Implement approval processing:
        1. Validate approver permissions
        2. Check approval requirements
        3. Handle multi-approver scenarios
        4. Send notifications
        5. Trigger execution if fully approved
        """
        approval_request = self.approval_requests.get(request_id)
        
        if not approval_request or approval_request.status != ApprovalStatus.PENDING:
            return False
        
        # Check if approver is eligible
        if approver not in approval_request.approvers:
            return False
        
        # Check if expired
        if datetime.utcnow() > approval_request.expires_at:
            approval_request.status = ApprovalStatus.EXPIRED
            return False
        
        # Approve the request
        approval_request.status = ApprovalStatus.APPROVED
        approval_request.approved_by = approver
        approval_request.approved_at = datetime.utcnow()
        
        # TODO: Send approval notifications
        self._notify_approval_decision(approval_request, "APPROVED", comments)
        
        return True
    
    def reject_request(self, request_id: str, approver: str, reason: str) -> bool:
        """
        Reject an operational request
        
        TODO: Implement rejection processing:
        1. Validate approver permissions
        2. Record rejection reason
        3. Send notifications
        4. Handle appeals process
        """
        approval_request = self.approval_requests.get(request_id)
        
        if not approval_request or approval_request.status != ApprovalStatus.PENDING:
            return False
        
        # Check if approver is eligible
        if approver not in approval_request.approvers:
            return False
        
        # Reject the request
        approval_request.status = ApprovalStatus.REJECTED
        approval_request.rejection_reason = reason
        
        # TODO: Send rejection notifications
        self._notify_approval_decision(approval_request, "REJECTED", reason)
        
        return True
    
    def _get_eligible_approvers(self, risk_level: str, environment: str) -> List[str]:
        """
        Determine eligible approvers based on risk and environment
        
        TODO: Implement dynamic approver selection:
        1. Query organizational hierarchy
        2. Check current availability
        3. Handle delegation rules
        4. Consider timezone and working hours
        """
        policy = self.approval_policies.get(risk_level, self.approval_policies["HIGH"])
        base_approvers = policy.get("eligible_approvers", ["ops_manager"])
        
        # Environment-specific approvers
        if environment == "prod":
            # Production requires higher-level approval
            if risk_level in ["HIGH", "CRITICAL"]:
                base_approvers.extend(["cto", "vp_engineering"])
        
        return list(set(base_approvers))  # Remove duplicates
    
    def _notify_approvers(self, approval_request: ApprovalRequest):
        """
        Send notifications to approvers
        
        TODO: Implement notification system:
        1. Send Slack messages
        2. Send email notifications
        3. Create approval dashboard entries
        4. Set up mobile push notifications
        5. Handle notification preferences
        """
        print(f"🔔 Approval needed for request {approval_request.request_id}")
        print(f"   Operation: {approval_request.operation_summary}")
        print(f"   Risk Level: {approval_request.risk_level}")
        print(f"   Requester: {approval_request.requester}")
        print(f"   Approvers: {', '.join(approval_request.approvers)}")
        print(f"   Expires: {approval_request.expires_at}")
    
    def _notify_approval_decision(self, approval_request: ApprovalRequest, decision: str, comments: str):
        """
        Send notifications about approval decision
        
        TODO: Implement decision notifications:
        1. Notify requester of decision
        2. Update approval dashboard
        3. Trigger next steps if approved
        4. Log decision for audit trail
        """
        print(f"✅ Request {approval_request.request_id} {decision}")
        print(f"   Decision by: {approval_request.approved_by}")
        print(f"   Comments: {comments}")
    
    def get_pending_approvals(self, approver: str) -> List[ApprovalRequest]:
        """
        Get pending approval requests for a specific approver
        
        TODO: Implement approver dashboard:
        1. Filter by approver permissions
        2. Sort by priority and expiration
        3. Include operation context
        4. Show approval history
        """
        pending = []
        for request in self.approval_requests.values():
            if (request.status == ApprovalStatus.PENDING and 
                approver in request.approvers and
                datetime.utcnow() <= request.expires_at):
                pending.append(request)
        
        return sorted(pending, key=lambda x: x.expires_at)
