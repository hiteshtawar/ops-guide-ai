# Cancel Order Runbook

**Task ID**: CANCEL_ORDER  
**Version**: 3.1  
**Last Updated**: 2024-12-01  
**Service**: Order Management  

## Overview

Complete cancellation of an order including cleanup of associated workflows, notifications, and billing records.

## Pre-checks

1. **Authorization Check**
   ```bash
   # Verify user has order_admin or ops_engineer role
   GET /api/v2/users/{user_id}/roles
   ```

2. **Order Status Validation**
   ```bash
   # Order must be in cancellable state
   GET /api/v2/orders/{order_id}/status
   # Valid states: pending, in_progress, on_hold
   # Invalid states: completed, cancelled, archived
   ```

3. **Business Rule Checks**
   ```bash
   # Check for billing holds or active shipments
   GET /api/v2/orders/{order_id}/dependencies
   # Ensure no billing_hold: true
   # Ensure shipment_status != "in_transit"
   ```

4. **Cancellation Window**
   ```bash
   # Verify within business hours (if required)
   # Check order age < 30 days for automatic approval
   GET /api/v2/orders/{order_id}/metadata
   ```

## Procedure

1. **Generate Idempotency Key**
   ```bash
   IDEMPOTENCY_KEY=$(uuidgen)
   ```

2. **Preview Cancellation Impact**
   ```bash
   GET /api/v2/orders/{order_id}/cancel/preview
   Headers:
     Authorization: Bearer {token}
     X-User-ID: {user_id}
   ```

3. **Execute Cancellation**
   ```bash
   POST /api/v2/orders/{order_id}/cancel
   Headers:
     Authorization: Bearer {token}
     X-User-ID: {user_id}
     X-Idempotency-Key: {IDEMPOTENCY_KEY}
     Content-Type: application/json
   
   Body:
   {
     "reason": "operational_request",
     "notes": "Cancelled via OpsGuide",
     "notify_stakeholders": true
   }
   ```

4. **Wait for Async Processing**
   ```bash
   # Poll status every 30 seconds, max 5 minutes
   GET /api/v2/orders/{order_id}/cancel/status
   # Expected: status="processing" -> status="completed"
   ```

## Rollback Procedure

**Within 2 hours of cancellation:**

1. **Check Reinstatement Eligibility**
   ```bash
   GET /api/v2/orders/{order_id}/reinstate/eligibility
   ```

2. **Reinstate Order** (if eligible)
   ```bash
   POST /api/v2/orders/{order_id}/reinstate
   Headers:
     Authorization: Bearer {token}
     X-User-ID: {user_id}
     X-Idempotency-Key: {new_uuid}
   
   Body:
   {
     "reason": "rollback_cancellation",
     "restore_previous_state": true
   }
   ```

**After 2 hours:**
- Reinstatement requires manual intervention
- Create remediation ticket with template: CASE-REINSTATE
- Include original order data from audit log

## Post-checks

1. **Verify Order Status**
   ```bash
   GET /api/v2/orders/{order_id}/status
   # Expected: status="cancelled"
   ```

2. **Check Downstream Systems**
   ```bash
   # Verify billing system updated
   GET /api/v2/billing/orders/{order_id}/status
   
   # Verify notification sent
   GET /api/v2/notifications/orders/{order_id}/history
   ```

3. **Audit Log Entry**
   ```bash
   GET /api/v2/orders/{order_id}/audit-log
   # Verify cancellation event recorded with user_id and timestamp
   ```

## Error Handling

**Common Errors:**

- `400 Bad Request - Invalid order state`: Check pre-conditions, order may already be cancelled
- `403 Forbidden - Insufficient permissions`: Verify user roles and order ownership
- `409 Conflict - Billing hold active`: Resolve billing issues first
- `429 Too Many Requests`: Wait 60 seconds and retry with same idempotency key

**Escalation Path:**
- Level 1: Retry with exponential backoff
- Level 2: Check order dependencies and resolve blocks
- Level 3: Contact order management team via #order-ops channel

## Risk Assessment

**Risk Level**: Medium

**Potential Impact**:
- Billing reconciliation required
- Customer notifications triggered
- Downstream system cleanup needed

**Mitigation**:
- Preview step shows impact before execution
- 2-hour rollback window available
- Full audit trail maintained
