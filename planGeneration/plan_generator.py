"""
Plan Generator - Orchestrates AI plan generation with context and constraints
"""
from typing import List, Dict, Any
from models import OperationalRequest, ClassificationResult, TaskId
from knowledgeRetrieval.vector_search import VectorSearchResult
from .claude_client import ClaudeClient
from .prompt_templates import PromptTemplateManager


class OperationalPlan:
    """Represents a complete operational plan"""
    def __init__(self, plan_data: Dict[str, Any]):
        self.summary = plan_data.get("summary", "")
        self.risk_level = plan_data.get("risk_level", "MEDIUM")
        self.requires_approval = plan_data.get("requires_approval", True)
        self.estimated_duration = plan_data.get("estimated_duration", "Unknown")
        self.pre_checks = plan_data.get("pre_checks", [])
        self.procedure = plan_data.get("procedure", [])
        self.post_checks = plan_data.get("post_checks", [])
        self.rollback = plan_data.get("rollback", [])
        self.citations = plan_data.get("citations", [])


class PlanGenerator:
    """Generates operational plans using AI and retrieved knowledge"""
    
    def __init__(self):
        self.claude_client = ClaudeClient()
        self.prompt_manager = PromptTemplateManager()
    
    async def generate_operational_plan(
        self,
        request: OperationalRequest,
        classification: ClassificationResult,
        knowledge_results: List[VectorSearchResult],
        policy_constraints: Dict[str, Any] = None
    ) -> OperationalPlan:
        """
        Generate complete operational plan using AI
        
        TODO: Implement full plan generation pipeline:
        1. Build context from knowledge retrieval results
        2. Select appropriate prompt template
        3. Generate plan using Claude
        4. Validate and structure response
        5. Add citations and metadata
        """
        
        # Build context from retrieved knowledge
        context = self._build_knowledge_context(knowledge_results)
        
        # Get prompt template for task type
        prompt = self.prompt_manager.build_prompt(
            request=request,
            classification=classification,
            context=context,
            constraints=policy_constraints or {}
        )
        
        # Generate plan using Claude
        raw_response = await self.claude_client.generate_plan(prompt)
        
        # Parse and structure the response
        plan_data = self._parse_plan_response(raw_response, knowledge_results)
        
        return OperationalPlan(plan_data)
    
    def _build_knowledge_context(self, knowledge_results: List[VectorSearchResult]) -> str:
        """
        Build context string from retrieved knowledge chunks
        
        TODO: Implement smart context building:
        1. Rank results by relevance score
        2. Deduplicate similar content
        3. Maintain source attribution
        4. Optimize for token limits
        """
        if not knowledge_results:
            return "No specific knowledge retrieved for this task."
        
        context_parts = []
        for i, result in enumerate(knowledge_results[:5]):  # Limit to top 5 results
            context_parts.append(f"""
Source {i+1}: {result.source_uri}
Relevance: {result.score:.2f}
Content: {result.content[:500]}...
""")
        
        return "\n".join(context_parts)
    
    def _parse_plan_response(
        self, 
        raw_response: str, 
        knowledge_results: List[VectorSearchResult]
    ) -> Dict[str, Any]:
        """
        Parse Claude response into structured plan data
        
        TODO: Implement robust response parsing:
        1. Handle different response formats
        2. Extract structured data from natural language
        3. Validate API calls and procedures
        4. Add error handling for malformed responses
        """
        try:
            import json
            plan_data = json.loads(raw_response)
            
            # Add citations from knowledge sources
            citations = []
            for result in knowledge_results:
                citations.append({
                    "source": result.source_uri,
                    "relevance_score": result.score,
                    "section": result.metadata.get("section", "unknown")
                })
            
            plan_data["citations"] = citations
            return plan_data
            
        except json.JSONDecodeError:
            # Fallback: try to extract structured data from natural language
            return self._extract_plan_from_text(raw_response, knowledge_results)
    
    def _extract_plan_from_text(
        self, 
        text_response: str, 
        knowledge_results: List[VectorSearchResult]
    ) -> Dict[str, Any]:
        """
        Extract plan structure from natural language response
        
        TODO: Implement NLP-based plan extraction:
        1. Parse natural language into structured steps
        2. Extract API calls and parameters
        3. Identify pre-checks and post-checks
        4. Determine risk levels and approval requirements
        """
        # Fallback plan structure
        return {
            "summary": "Generated plan from natural language response",
            "risk_level": "MEDIUM",
            "requires_approval": True,
            "estimated_duration": "Unknown",
            "pre_checks": [],
            "procedure": [
                {
                    "step": 1,
                    "name": "Execute Operation",
                    "description": text_response[:200] + "...",
                    "action": "Follow retrieved knowledge guidance"
                }
            ],
            "post_checks": [],
            "rollback": [],
            "citations": [{"source": r.source_uri} for r in knowledge_results]
        }
