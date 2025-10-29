"""
Pattern-based request classification using regex
"""
import re
from typing import Optional
from models import OperationalRequest, ClassificationResult, UseCase, TaskId
from .entity_extractor import EntityExtractor


class PatternClassifier:
    """Classifies operational requests using regex pattern matching"""
    
    def __init__(self):
        # Task identification patterns
        self.task_patterns = {
            TaskId.CANCEL_ORDER: [
                r'\bcancel\b.*\border\b',
                r'\border\b.*\bcancel\b',
                r'\bterminate\b.*\border\b',
                r'\babort\b.*\border\b',
                r'\bstop\b.*\border\b'
            ],
            TaskId.CANCEL_CASE: [
                r'\bcancel\b.*\bcase\b',
                r'\bcase\b.*\bcancel\b',
                r'\bterminate\b.*\bcase\b',
                r'\babort\b.*\bcase\b',
                r'\bstop\b.*\bcase\b',
                r'\bclose\b.*\bcase\b',
                r'\bcase\b.*\bclose\b'
            ],
            TaskId.CHANGE_ORDER_STATUS: [
                r'\bchange\b.*\bstatus\b',
                r'\bstatus\b.*\bchange\b',
                r'\bupdate\b.*\bstatus\b',
                r'\btransition\b.*\border\b',
                r'\bmove\b.*\border\b.*\bto\b',
                r'\bset\b.*\bstatus\b'
            ]
        }
        
        # Environment detection patterns
        self.env_patterns = {
            'dev': [r'\bdev\b', r'\bdevelopment\b', r'\bdev-\w+\b'],
            'staging': [r'\bstaging\b', r'\bstage\b', r'\bstg\b'],
            'prod': [r'\bprod\b', r'\bproduction\b', r'\bprd\b']
        }
        
        # Service detection patterns
        self.service_patterns = {
            'Order': [r'\border\b', r'\borders\b', r'\border management\b'],
            'Case': [r'\bcase\b', r'\bcases\b', r'\bcase management\b'],
            'Fulfillment': [r'\bfulfillment\b', r'\bshipping\b', r'\bdelivery\b'],
            'Billing': [r'\bbilling\b', r'\binvoice\b', r'\bpayment\b']
        }
        
        self.entity_extractor = EntityExtractor()

    def classify(self, request: OperationalRequest) -> ClassificationResult:
        """Classify an operational request using pattern matching"""
        query_lower = request.query.lower()
        
        # For MVP, we only handle U2 (Operational Ask)
        use_case = UseCase.OPERATIONAL_ASK
        
        # Identify specific task using pattern matching
        task_id = self._identify_task(query_lower)
        
        # Extract entities from the query
        environment = self._extract_environment(query_lower, request.environment)
        service = self._extract_service(query_lower)
        order_id = self.entity_extractor.extract_order_id(request.query) if 'order' in query_lower else None
        case_id = self.entity_extractor.extract_case_id(request.query) if 'case' in query_lower else None
        target_status = self.entity_extractor.extract_target_status(request.query) if task_id == TaskId.CHANGE_ORDER_STATUS else None
        
        # Build extracted entities dict
        extracted_entities = {
            "service": service,
            "target_status": target_status
        }
        if order_id:
            extracted_entities["order_id"] = order_id
        if case_id:
            extracted_entities["case_id"] = case_id
        
        # Calculate confidence based on pattern matches
        confidence = 0.9 if task_id else 0.5
        
        return ClassificationResult(
            use_case=use_case,
            task_id=task_id,
            confidence=confidence,
            extracted_entities=extracted_entities,
            environment=environment,
            service=service
        )

    def _identify_task(self, query: str) -> Optional[TaskId]:
        """Identify the specific task type using regex patterns"""
        for task_id, patterns in self.task_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return task_id
        
        # Fallback logic - if contains "order" and operational keywords
        if 'order' in query and any(word in query for word in ['change', 'update', 'fix', 'cancel', 'modify']):
            if any(word in query for word in ['cancel', 'terminate', 'abort', 'stop']):
                return TaskId.CANCEL_ORDER
            elif any(word in query for word in ['status', 'state', 'transition']):
                return TaskId.CHANGE_ORDER_STATUS
        
        # Fallback logic - if contains "case" and cancel keywords
        if 'case' in query and any(word in query for word in ['cancel', 'terminate', 'abort', 'stop', 'close']):
            return TaskId.CANCEL_CASE
        
        return None

    def _extract_environment(self, query: str, default_env: str) -> str:
        """Extract target environment using regex patterns"""
        for env, patterns in self.env_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return env
        return default_env

    def _extract_service(self, query: str) -> str:
        """Extract target service using regex patterns"""
        for service, patterns in self.service_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return service
        # Default based on query content
        if 'case' in query.lower():
            return "Case"
        return "Order"  # Default to Order service
