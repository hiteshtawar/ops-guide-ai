"""
Core data models for OpsGuide MVP
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class UseCase(str, Enum):
    """OpsGuide use cases"""
    OPERATIONAL_ASK = "U2"


class RequestStatus(str, Enum):
    """Request processing status"""
    RECEIVED = "received"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskId(str, Enum):
    """Known operational tasks for MVP"""
    CANCEL_ORDER = "CANCEL_ORDER"
    CHANGE_ORDER_STATUS = "CHANGE_ORDER_STATUS"


class OperationalRequest(BaseModel):
    """Incoming operational request"""
    request_id: str = Field(..., description="Unique request identifier")
    user_id: str = Field(..., description="User making the request")
    query: str = Field(..., description="Natural language request")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    environment: Optional[str] = Field(default="dev", description="Target environment")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ClassificationResult(BaseModel):
    """Request classification result"""
    use_case: UseCase = Field(..., description="Identified use case")
    task_id: Optional[TaskId] = Field(None, description="Specific task if identified")
    confidence: float = Field(..., description="Classification confidence")
    extracted_entities: Dict[str, Any] = Field(default_factory=dict, description="Extracted entities")
    environment: Optional[str] = Field(None, description="Target environment")
    service: Optional[str] = Field(None, description="Target service")
