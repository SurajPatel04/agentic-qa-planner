from typing import Any, Dict
from app.graphs.state import QAState
from app.services.vector_store import VectorStoreService


def retrieve_qa_docs(state: QAState, vector_service: VectorStoreService) -> Dict[str, Any]:
    """
    Node 1: Retrieves QA guidelines based on the user story and change summary.
    """
    query = f"""
Requirement:
{state.get('user_story', '')}

Acceptance Criteria:
{chr(10).join(f"- {ac}" for ac in state.get('acceptance_criteria', []))}

Implementation Summary:
{state.get('implementation_summary', '')}
"""
    docs = vector_service.similarity_search(query, top_k=5)
    
    log_entry = {
        "execution_order": 1,
        "node": "Retrieve QA Docs",
        "status": "Success",
        "message": f"Retrieved {len(docs)} QA documents.",
        "sources": [doc.metadata.get("filename", "unknown.md") for doc in docs]
    }
    
    return {
        "retrieved_docs": docs,
        "execution_log": [log_entry]
    }
