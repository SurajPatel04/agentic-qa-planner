from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from app.graphs.state import QAState
from app.graphs.schema import TestCaseSchema, TestGenerationOutput
from app.utils.llm import get_openai_llm

llm = get_openai_llm()

def generate_test_cases(state: QAState) -> Dict[str, Any]:
    """
    Node 3: Generates comprehensive test cases based on the analyzed state.
    """
    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            """You are a Senior SDET. Generate a comprehensive suite of test cases (Unit, API, Integration, E2E, Playwright, Manual) ensuring all Acceptance Criteria, user flows, assumptions, and risks are thoroughly covered. Strictly follow the provided QA Guidelines. IMPORTANT: Your job is only to propose the tests. Do not mark the feature as release-ready or passed."""
        ),
        HumanMessagePromptTemplate.from_template(
            """User Story:
{user_story}

Acceptance Criteria:
{acceptance_criteria}

Identified User Flows:
{user_flows}

Assumptions:
{assumptions}

Identified Risks:
{risks}

QA Guidelines (Context):
{qa_guidelines}"""
        )
    ])
    
    qa_guidelines = "\n---\n".join([doc.page_content for doc in state.get("retrieved_docs", [])])
    ac_text = "\n".join([f"- {ac}" for ac in state.get("acceptance_criteria", [])])
    flows_text = "\n".join([f"- {flow}" for flow in state.get("user_flows", [])])
    assumptions_text = "\n".join([f"- {a}" for a in state.get("assumptions", [])])
    risks_text = "\n".join([f"- {r}" for r in state.get("risks", [])])
    
    chain = prompt | llm.with_structured_output(TestGenerationOutput)
    
    response = chain.invoke({
        "user_story": state.get("user_story", ""),
        "acceptance_criteria": ac_text,
        "user_flows": flows_text,
        "assumptions": assumptions_text,
        "risks": risks_text,
        "qa_guidelines": qa_guidelines
    })
    
    log_entry = {
        "execution_order": 3,
        "node": "Generate Test Cases",
        "status": "Success",
        "message": f"Generated {len(response.test_cases)} test cases."
    }
    
    return {
        "test_cases": response.test_cases,
        "execution_log": [log_entry]
    }
