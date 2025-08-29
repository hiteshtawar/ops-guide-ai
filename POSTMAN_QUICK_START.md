# Postman Quick Start Guide

## 🚀 One-Minute Setup

### 1. Start System
```bash
docker-compose up -d opsguide-core
```

### 2. Import Collection
- Download: `OpsGuide-API-Tests.postman_collection.json`
- Import into Postman
- Collection includes 20+ automated tests

### 3. Run All Tests
- Select **OpsGuide API Tests** collection
- Click **Run** → **Run Collection**
- Watch 20+ tests execute automatically

## 📋 Test Categories

| Category | Tests | Purpose |
|----------|-------|---------|
| **Health Checks** | 2 tests | System availability |
| **Cancel Order** | 3 tests | Order cancellation patterns |
| **Change Status** | 4 tests | Status change variants |
| **Edge Cases** | 3 tests | Error handling |
| **Environment** | 2 tests | Dev/prod context |
| **Performance** | 1 test | Response time (<500ms) |

## ✅ Expected Results

- **Success Rate**: 100% (20+ tests pass)
- **Response Time**: <500ms for pattern matching
- **Accuracy**: 90% on valid operational requests
- **Confidence**: 0.9 for recognized patterns, 0.5 for edge cases

## 🔧 Key Test Examples

### Cancel Order
```json
{
  "query": "cancel order ORDER-2024-001",
  "environment": "dev"
}
```
**Expected**: `task_id: "CANCEL_ORDER"`, `confidence: 0.9`

### Change Order Status
```json
{
  "query": "change order status to completed for ORDER-456",
  "environment": "prod"
}
```
**Expected**: `task_id: "CHANGE_ORDER_STATUS"`, `target_status: "completed"`

### Edge Case
```json
{
  "query": "do something random",
  "environment": "dev"
}
```
**Expected**: `task_id: null`, `confidence: 0.5`

## 🛑 Cleanup
```bash
docker-compose down
```

## 📚 Full Documentation
See [README.md](./README.md#testing-with-postman) for complete testing guide.
