"""
Knowledge Indexer for processing and indexing runbooks and API specs
"""
import os
import re
from typing import List, Dict, Any
from pathlib import Path


class KnowledgeChunk:
    """Represents a chunk of knowledge content"""
    def __init__(self, content: str, metadata: Dict[str, Any], source_uri: str):
        self.content = content
        self.metadata = metadata
        self.source_uri = source_uri


class KnowledgeIndexer:
    """Processes knowledge files and creates searchable chunks"""
    
    def __init__(self, knowledge_dir: str = "knowledge"):
        self.knowledge_dir = knowledge_dir
    
    def process_knowledge_base(self) -> List[KnowledgeChunk]:
        """
        Process all knowledge files and create chunks
        
        TODO: Implement comprehensive knowledge processing:
        1. Scan knowledge directory for markdown files
        2. Parse runbooks and API specs
        3. Extract sections and create chunks
        4. Add metadata (task_id, section, environment)
        5. Handle different file formats
        """
        chunks = []
        
        # Process runbooks
        runbooks_dir = Path(self.knowledge_dir) / "runbooks"
        if runbooks_dir.exists():
            for file_path in runbooks_dir.glob("*.md"):
                file_chunks = self._process_runbook(file_path)
                chunks.extend(file_chunks)
        
        # Process API specs
        api_specs_dir = Path(self.knowledge_dir) / "api-specs"
        if api_specs_dir.exists():
            for file_path in api_specs_dir.glob("*.md"):
                file_chunks = self._process_api_spec(file_path)
                chunks.extend(file_chunks)
        
        return chunks
    
    def _process_runbook(self, file_path: Path) -> List[KnowledgeChunk]:
        """
        Process a runbook file and extract chunks
        
        TODO: Implement smart chunking:
        1. Parse markdown structure (headers, sections)
        2. Extract task_id from filename or content
        3. Create chunks for each section
        4. Preserve context and relationships
        """
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract task_id from filename
            task_id = self._extract_task_id_from_filename(file_path.name)
            
            # Simple chunking by sections for now
            sections = self._split_by_headers(content)
            
            for i, section in enumerate(sections):
                if section.strip():
                    chunk = KnowledgeChunk(
                        content=section.strip(),
                        metadata={
                            "task_id": task_id,
                            "file_type": "runbook",
                            "section_index": i,
                            "source_file": file_path.name
                        },
                        source_uri=str(file_path)
                    )
                    chunks.append(chunk)
        
        except Exception as e:
            print(f"Error processing runbook {file_path}: {e}")
        
        return chunks
    
    def _process_api_spec(self, file_path: Path) -> List[KnowledgeChunk]:
        """
        Process an API specification file
        
        TODO: Implement API spec parsing:
        1. Extract endpoints and methods
        2. Parse request/response schemas
        3. Create chunks for each endpoint
        4. Add metadata for API operations
        """
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple chunking for API specs
            sections = self._split_by_headers(content)
            
            for i, section in enumerate(sections):
                if section.strip():
                    chunk = KnowledgeChunk(
                        content=section.strip(),
                        metadata={
                            "file_type": "api_spec",
                            "section_index": i,
                            "source_file": file_path.name
                        },
                        source_uri=str(file_path)
                    )
                    chunks.append(chunk)
        
        except Exception as e:
            print(f"Error processing API spec {file_path}: {e}")
        
        return chunks
    
    def _extract_task_id_from_filename(self, filename: str) -> str:
        """Extract task ID from filename"""
        if "cancel-case" in filename.lower():
            return "CANCEL_CASE"
        elif "change-case-status" in filename.lower():
            return "CHANGE_CASE_STATUS"
        elif "reconcile-case" in filename.lower():
            return "RECONCILE_CASE_DATA"
        return "UNKNOWN"
    
    def _split_by_headers(self, content: str) -> List[str]:
        """
        Split content by markdown headers
        
        TODO: Implement smart content splitting:
        1. Respect markdown structure
        2. Maintain context between sections
        3. Handle code blocks and tables
        4. Optimize chunk sizes for embeddings
        """
        # Simple split by ## headers for now
        sections = re.split(r'\n## ', content)
        return sections
