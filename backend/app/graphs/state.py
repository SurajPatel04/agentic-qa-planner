import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict
from pydantic import BaseModel, Field
from langchain_core.documents import Document

from app.graphs.schema import TestCaseSchema



# ==========================================
# LangGraph State Schema
# ==========================================

class QAState(TypedDict):
    """
    State object passed between nodes in the Agentic QA Planner workflow.
    """
    # --- 1. Inputs (Provided by Developer) ---
    user_story: str
    acceptance_criteria: List[str]
    implementation_summary: str
    
    # --- 2. Retrieved Context ---
    # `operator.add` allows appending if multiple retrieval nodes run, otherwise overwrites if not used.
    # Usually, a single retriever node will just return the list.
    retrieved_docs: List[Document]
    
    # --- 3. Flow Identification ---
    user_flows: List[str]
    
    # --- 4. Test Generation ---
    test_cases: List[TestCaseSchema]
    
    # Assumptions made by the LLM when context is incomplete
    assumptions: List[str]
    
    # Risks identified by the LLM during analysis
    risks: List[str]
    
    # --- Internal Graph Management ---
    # --- 5. Graph Output / Metadata ---
    # Captures missing rationales, empty steps, etc.
    errors: Annotated[List[str], operator.add]
    
    # Structured execution logs for DB persistence
    execution_log: Annotated[List[Dict[str, Any]], operator.add]
