from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from app.graphs.state import QAState
from app.utils.llm import get_openai_llm

llm = get_openai_llm()

from app.graphs.schema import AnalysisOutput


def analyze_requirement(state: QAState) -> Dict[str, Any]:
    """
    Node 2: Analyzes requirements to extract user flows, assumptions, and risks.
    """
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            """You are an expert QA Architect. Analyze the provided requirements, changes, and QA guidelines. Identify the main user flows, explicitly state any assumptions about missing context, and highlight potential risks, edge cases, or regression areas."""
        ),
        HumanMessagePromptTemplate.from_template(
            """User Story:
{user_story}

Acceptance Criteria:
{acceptance_criteria}

Implementation Summary:
{implementation_summary}

QA Guidelines (Context):
{qa_guidelines}"""
        )
    ])
    
    qa_guidelines = "\n---\n".join([doc.page_content for doc in state.get("retrieved_docs", [])])
    ac_text = "\n".join([f"- {ac}" for ac in state.get("acceptance_criteria", [])])
    
    chain = prompt | llm.with_structured_output(AnalysisOutput)
    
    response = chain.invoke({
        "user_story": state.get("user_story", ""),
        "acceptance_criteria": ac_text,
        "implementation_summary": state.get("implementation_summary", ""),
        "qa_guidelines": qa_guidelines
    })
    
    log_entry = {
        "execution_order": 2,
        "node": "Analyze Requirement",
        "status": "Success",
        "message": f"Generated {len(response.user_flows)} user flows and identified {len(response.risks)} risks."
    }
    
    return {
        "user_flows": response.user_flows,
        "assumptions": response.assumptions,
        "risks": response.risks,
        "execution_log": [log_entry]
    }
