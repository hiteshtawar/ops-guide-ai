# Order Management API Specification

**Version**: 2.1  
**Base URL**: `https://api.example.com/v2`  
**Authentication**: Bearer Token  
**Rate Limits**: 100 requests/minute per user  

## Common Headers

All requests should include:
```
Authorization: Bearer {jwt_token}
X-User-ID: {user_id}
Content-Type: application/json
X-Idempotency-Key: {uuid} (for mutations)
```

## Order Status Operations

### GET /orders/{order_id}/status

Get current order status and metadata.

**Parameters**:
- `order_id` (path, required): UUID of the order

**Response**:
```json
{
  "order_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "in_progress",
  "created_at": "2024-12-01T10:00:00Z",
  "updated_at": "2024-12-01T14:30:00Z",
  "assigned_to": "pathologist_123",
  "metadata": {
    "age_days": 5,
    "priority": "normal",
    "environment": "prod"
  }
}
```

**Error Codes**:
- `404`: Order not found
- `403`: Insufficient permissions

---

### PATCH /orders/{order_id}/status

Change order status following business rules.

**Parameters**:
- `order_id` (path, required): UUID of the order

**Request Body**:
```json
{
  "status": "completed",
  "reason": "pathologist_signoff",
  "notes": "Order completed successfully",
  "artifacts": {
    "signature": "digital_signature_data",
    "report_id": "report_456"
  }
}
```

**Response**:
```json
{
  "order_id": "123e4567-e89b-12d3-a456-426614174000",
  "previous_status": "in_progress",
  "new_status": "completed",
  "transition_id": "trans_789",
  "timestamp": "2024-12-01T15:00:00Z"
}
```

**Error Codes**:
- `400`: Invalid transition or missing required fields
- `403`: User lacks required role for this transition
- `409`: Concurrent modification or business rule violation
- `422`: Missing required artifacts

---

### POST /orders/{order_id}/cancel

Cancel a order and trigger cleanup workflows.

**Parameters**:
- `order_id` (path, required): UUID of the order

**Request Body**:
```json
{
  "reason": "operational_request",
  "notes": "Cancelled due to data quality issues",
  "notify_stakeholders": true
}
```

**Response**:
```json
{
  "order_id": "123e4567-e89b-12d3-a456-426614174000",
  "cancellation_id": "cancel_123",
  "status": "processing",
  "estimated_completion": "2024-12-01T15:05:00Z",
  "rollback_deadline": "2024-12-01T17:00:00Z"
}
```

**Error Codes**:
- `400`: Order in non-cancellable state
- `403`: Insufficient permissions
- `409`: Billing hold or active dependencies
- `429`: Rate limit exceeded

---

### GET /orders/{order_id}/cancel/preview

Preview the impact of cancelling a order without executing.

**Parameters**:
- `order_id` (path, required): UUID of the order

**Response**:
```json
{
  "order_id": "123e4567-e89b-12d3-a456-426614174000",
  "impact_assessment": {
    "billing_affected": true,
    "notifications_count": 3,
    "downstream_systems": ["billing", "reporting", "notifications"],
    "estimated_duration": "2-5 minutes",
    "rollback_available": true,
    "rollback_deadline": "2024-12-01T17:00:00Z"
  },
  "warnings": [
    "This order has active billing records",
    "Customer notifications will be sent"
  ]
}
```

---

### POST /orders/{order_id}/reinstate

Reinstate a cancelled order (within rollback window).

**Parameters**:
- `order_id` (path, required): UUID of the order

**Request Body**:
```json
{
  "reason": "rollback_cancellation",
  "restore_previous_state": true,
  "notes": "Cancelled in error"
}
```

**Response**:
```json
{
  "order_id": "123e4567-e89b-12d3-a456-426614174000",
  "reinstatement_id": "reinstate_456",
  "restored_status": "in_progress",
  "timestamp": "2024-12-01T15:30:00Z"
}
```

**Error Codes**:
- `400`: Order not in cancelled state or outside rollback window
- `403`: Insufficient permissions
- `409`: Downstream systems already processed cancellation

---

## Data Reconciliation Operations

### GET /orders/{order_id}/reconcile/preview

Preview data divergence between systems without making changes.

**Parameters**:
- `order_id` (path, required): UUID of the order

**Response**:
```json
{
  "order_id": "123e4567-e89b-12d3-a456-426614174000",
  "divergences": [
    {
      "field": "status",
      "lab_system": "in_progress",
      "downstream_system": "pending",
      "severity": "medium"
    },
    {
      "field": "assigned_pathologist",
      "lab_system": "dr_smith",
      "downstream_system": null,
      "severity": "low"
    }
  ],
  "recommended_actions": [
    "Update downstream status to match lab system",
    "Sync pathologist assignment"
  ],
  "risk_assessment": "low"
}
```

---

### POST /orders/{order_id}/reconcile

Execute data reconciliation to fix divergence.

**Parameters**:
- `order_id` (path, required): UUID of the order

**Request Body**:
```json
{
  "reconcile_fields": ["status", "assigned_pathologist"],
  "source_of_truth": "lab_system",
  "notes": "Fixing data divergence identified in incident"
}
```

**Response**:
```json
{
  "order_id": "123e4567-e89b-12d3-a456-426614174000",
  "reconciliation_id": "recon_789",
  "status": "completed",
  "changes_applied": [
    {
      "field": "status",
      "old_value": "pending",
      "new_value": "in_progress",
      "system": "downstream"
    }
  ],
  "timestamp": "2024-12-01T16:00:00Z"
}
```

## Authentication & Authorization

**Scopes Required**:
- `order:read` - Read order information
- `order:status:write` - Change order status
- `order:cancel` - Cancel orders
- `order:reconcile` - Fix data divergence

**Role Requirements**:
- `lab_tech` - Basic order operations
- `pathologist` - Medical decisions, sign-offs
- `order_admin` - Administrative operations, cancellations
- `ops_engineer` - System operations, reconciliation
- `qa_reviewer` - Quality assurance workflows

## Rate Limiting

- Standard operations: 100 requests/minute per user
- Bulk operations: 10 requests/minute per user
- Status changes: 20 requests/minute per order
- Cancellations: 5 requests/minute per user

**Rate Limit Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1701435600
```

## Idempotency

All mutation operations support idempotency via `X-Idempotency-Key` header:
- Use UUID v4 format
- Keys expire after 24 hours
- Same key returns cached response for successful operations
- Failed operations can be retried with same key

## Error Response Format

```json
{
  "error": {
    "code": "INVALID_TRANSITION",
    "message": "Cannot transition from 'completed' to 'pending'",
    "details": {
      "current_status": "completed",
      "requested_status": "pending",
      "valid_transitions": ["under_review"]
    },
    "request_id": "req_123456",
    "timestamp": "2024-12-01T16:30:00Z"
  }
}
```
