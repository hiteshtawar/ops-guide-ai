# Change Order Status Runbook

**Task ID**: CHANGE_ORDER_STATUS  
**Version**: 2.8  
**Last Updated**: 2024-12-01  
**Service**: Order Management  

## Overview

Transition an order from one status to another following business state machine rules and authorization requirements.

## Pre-checks

1. **Authorization Check**
   ```bash
   # Verify user has appropriate role for transition
   GET /api/v2/users/{user_id}/roles
   GET /api/v2/orders/{order_id}/transition-permissions
   ```

2. **Current Status Validation**
   ```bash
   GET /api/v2/orders/{order_id}/status
   # Record current status for rollback
   ```

3. **Valid Transition Check**
   ```bash
   # Verify requested transition is allowed
   GET /api/v2/orders/status-transitions
   # Check: current_status -> target_status is valid
   ```

4. **Required Artifacts**
   ```bash
   # Some transitions require specific data
   GET /api/v2/orders/{order_id}/requirements/{target_status}
   # e.g., "completed" status requires pathologist_signature
   ```

## Status Transition Matrix

| From | To | Required Role | Artifacts Needed |
|------|-----|---------------|------------------|
| pending | in_progress | lab_tech, pathologist | assignment_id |
| pending | on_hold | order_admin | hold_reason |
| in_progress | completed | pathologist | signature, report |
| in_progress | on_hold | pathologist, order_admin | hold_reason |
| on_hold | in_progress | pathologist | resolution_notes |
| on_hold | cancelled | order_admin | cancellation_reason |
| completed | under_review | qa_reviewer | review_reason |
| under_review | completed | qa_reviewer | approval_notes |

## Procedure

1. **Generate Idempotency Key**
   ```bash
   IDEMPOTENCY_KEY=$(uuidgen)
   ```

2. **Validate Transition**
   ```bash
   POST /api/v2/orders/{order_id}/status/validate
   Headers:
     Authorization: Bearer {token}
     X-User-ID: {user_id}
     Content-Type: application/json
   
   Body:
   {
     "target_status": "{new_status}",
     "reason": "{transition_reason}"
   }
   ```

3. **Execute Status Change**
   ```bash
   PATCH /api/v2/orders/{order_id}/status
   Headers:
     Authorization: Bearer {token}
     X-User-ID: {user_id}
     X-Idempotency-Key: {IDEMPOTENCY_KEY}
     Content-Type: application/json
   
   Body:
   {
     "status": "{new_status}",
     "reason": "{transition_reason}",
     "notes": "Changed via OpsGuide",
     "artifacts": {
       "signature": "{signature_data}",
       "assignment_id": "{assignment_id}"
     }
   }
   ```

4. **Verify Transition**
   ```bash
   GET /api/v2/orders/{order_id}/status
   # Confirm status changed successfully
   ```

## Rollback Procedure

**Immediate Rollback (within 30 minutes):**

1. **Check Reversibility**
   ```bash
   GET /api/v2/orders/{order_id}/status-history
   # Verify previous status and transition rules
   ```

2. **Reverse Transition**
   ```bash
   PATCH /api/v2/orders/{order_id}/status
   Headers:
     Authorization: Bearer {token}
     X-User-ID: {user_id}
     X-Idempotency-Key: {new_uuid}
   
   Body:
   {
     "status": "{previous_status}",
     "reason": "rollback_status_change",
     "notes": "Rolled back via OpsGuide"
   }
   ```

**Complex Rollback (after 30 minutes):**
- Some transitions create downstream effects
- May require compensating actions:
  - If completed → in_progress: notify stakeholders
  - If cancelled → in_progress: check billing implications
- Create remediation ticket if manual steps needed

## Post-checks

1. **Verify Status Change**
   ```bash
   GET /api/v2/orders/{order_id}/status
   # Expected: status="{target_status}"
   ```

2. **Check Audit Trail**
   ```bash
   GET /api/v2/orders/{order_id}/audit-log
   # Verify transition logged with user, timestamp, reason
   ```

3. **Validate Downstream Effects**
   ```bash
   # Check if notifications were sent
   GET /api/v2/notifications/orders/{order_id}/recent
   
   # Verify workflow updates
   GET /api/v2/workflows/orders/{order_id}/status
   ```

## Error Handling

**Common Errors:**

- `400 Bad Request - Invalid transition`: Check status transition matrix
- `403 Forbidden - Insufficient role`: User lacks required role for this transition
- `409 Conflict - Missing artifacts`: Required data not provided (e.g., signature)
- `422 Unprocessable Entity - Business rule violation`: Custom validation failed

**Escalation Path:**
1. Verify current order state and user permissions
2. Check if required artifacts are available
3. Review business rules with order management team
4. For persistent issues, escalate to #order-ops channel

## Risk Assessment

**Risk Level**: Low to Medium (depends on transition)

**Low Risk Transitions**:
- pending → in_progress
- in_progress → on_hold
- on_hold → in_progress

**Medium Risk Transitions**:
- in_progress → completed (affects billing)
- completed → under_review (may delay reporting)
- any_status → cancelled (cleanup required)

**Mitigation**:
- Validation step prevents invalid transitions
- Audit trail for all changes
- 30-minute rollback window for most transitions
- Required approvals for high-impact changes
