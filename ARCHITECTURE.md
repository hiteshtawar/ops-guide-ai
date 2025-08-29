# OpsGuide MVP Architecture

## Overview

This MVP demonstrates a clean, modular approach to operational request processing using **traditional programming techniques** rather than AI/ML dependencies.

## Architecture Flow

```
HTTP Request → Parsing & Validation → Pattern Classification → Entity Extraction → Structured Response
```

## Components

### 1. **parsingAndValidation/**
- **Purpose**: HTTP request handling and security validation
- **Technology**: Python standard library (json, http.server)
- **Key Functions**:
  - Parse HTTP headers and JSON body
  - Validate Authorization and X-User-ID headers
  - Extract content and generate request IDs

### 2. **requestClassification/**
- **Purpose**: Pattern-based task identification (NOT AI)
- **Technology**: Python regex (re module)
- **Key Functions**:
  - Match user queries against predefined patterns
  - Classify into CANCEL_CASE or CHANGE_CASE_STATUS
  - Extract entities (case_id, target_status, environment)

### 3. **models/**
- **Purpose**: Data structures and type safety
- **Technology**: Pydantic for validation
- **Key Models**:
  - OperationalRequest
  - ClassificationResult
  - TaskId enum

### 4. **knowledge/**
- **Purpose**: Reference documentation
- **Contents**:
  - Runbooks for operational procedures
  - API specifications for case management

## Why This Approach?

### ✅ Advantages
- **Fast**: Regex pattern matching is microseconds, not seconds
- **Deterministic**: Same input always produces same output
- **Debuggable**: Can see exactly which pattern matched
- **Cost-effective**: No API calls or model inference costs
- **Reliable**: No hallucination or unpredictable behavior

### ⚠️ Limitations
- **Manual Pattern Management**: Need to add patterns for new use cases
- **Limited Flexibility**: Can't handle complex variations automatically
- **No Learning**: Doesn't adapt to new patterns without code changes

## Pattern Matching Examples

### CANCEL_CASE Patterns
```python
r'\bcancel\b.*\bcase\b'      # "cancel case CASE-123"
r'\bcase\b.*\bcancel\b'      # "Please case cancel this"
r'\bterminate\b.*\bcase\b'   # "terminate case processing"
```

### CHANGE_CASE_STATUS Patterns
```python
r'\bchange\b.*\bstatus\b'    # "change case status"
r'\bupdate\b.*\bstatus\b'    # "update status to completed"
r'\bset\b.*\bstatus\b'       # "set status to pending"
```

## Entity Extraction

### Case ID Extraction
```python
r'CASE[_-](\d{4})[_-][\w-]+'  # CASE-2024-TEST-001 → "2024"
r'\bcase[_\s-]?(\d+)\b'       # case-12345 → "12345"
```

### Status Extraction
```python
'completed': [r'\bcomplete\b', r'\bfinish\b', r'\bdone\b']
'cancelled': [r'\bcancel\b', r'\babort\b', r'\bterminate\b']
```

## Confidence Scoring

```python
confidence = 0.9 if task_id else 0.5
```

- **0.9 (90%)**: High confidence when pattern matches
- **0.5 (50%)**: Low confidence when no pattern matches

## No AI Dependencies

This MVP intentionally avoids:
- ❌ Machine Learning models
- ❌ Large Language Models (LLMs)
- ❌ Vector embeddings
- ❌ AWS Bedrock/OpenAI APIs
- ❌ Complex NLP libraries

Instead it uses:
- ✅ Python standard library
- ✅ Regex pattern matching
- ✅ Pydantic for data validation
- ✅ Simple HTTP server

## Scalability Considerations

### When to Add AI
Consider AI/ML when:
- Pattern variations become too numerous to manage manually
- Need to handle typos and grammatical variations
- Require understanding of context and intent beyond keywords
- Need to learn from user feedback automatically

### Current Limitations
- Only handles 2 task types (CANCEL_CASE, CHANGE_CASE_STATUS)
- Limited to predefined patterns
- No learning or adaptation capabilities
- Manual effort required to add new use cases

## Deployment

```bash
# Local development
python server.py

# Docker
docker build -t opsguide-mvp .
docker run -p 8093:8093 opsguide-mvp

# Demo
./demo.sh
```
