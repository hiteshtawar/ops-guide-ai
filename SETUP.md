# Quick Setup Guide

## Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose** (for AI-enhanced mode)
- **curl** (for testing)

## Core System Setup (Recommended)

```bash
# 1. Clone repository
git clone <your-repo-url>
cd ops-guide-mvp

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start core server
python server.py

# 4. Test the system
./test-suite.sh
```

## AI-Enhanced System Setup

```bash
# 1. Install full dependencies
pip install -r requirements-full.txt

# 2. Start with Docker Compose
docker-compose up -d opsguide-ai

# 3. Test AI-enhanced system
curl -X POST http://localhost:8094/v1/request \
  -H "Content-Type: application/json" \
  -H "X-User-ID: test-user" \
  -H "Authorization: Bearer test-token" \
  -d '{"query": "cancel case CASE-2024-001", "environment": "dev"}'
```

## Docker Options

```bash
# Core system only (zero AI costs)
docker-compose up -d opsguide-core

# AI-enhanced system (premium features)
docker-compose up -d opsguide-ai

# Full stack (LocalStack + OpenSearch + AI)
docker-compose up -d
```

## Verification

### Core System Health Check
```bash
curl http://localhost:8093/health
```

### AI-Enhanced System Health Check  
```bash
curl http://localhost:8094/health
```

### Complete Testing with Postman
For comprehensive testing, use the provided Postman collection:

1. **Import Collection**: Import `OpsGuide-API-Tests.postman_collection.json`
2. **Run Tests**: Execute 20+ automated test cases
3. **Verify Results**: Check 90% accuracy on operational requests

See [Testing with Postman](./README.md#testing-with-postman) section in README for detailed steps.

## Troubleshooting

- **Port conflicts**: Change ports in docker-compose.yml
- **Docker issues**: Run `docker-compose down` then `docker-compose up -d`
- **Permission errors**: Check file permissions on shell scripts (`chmod +x test-suite.sh`)

## Cost Management

- **Core System**: $0 per request - recommended for production
- **AI-Enhanced**: ~$0.01-$0.10 per request - use for complex scenarios
- **Development**: Use LocalStack to avoid AWS charges during development
