import functools
from langgraph.graph import StateGraph, START, END

from app.graphs.state import QAState
from app.graphs.nodes import retrieve_qa_docs, analyze_requirement, generate_test_cases, validate_tests
from app.services.vector_store import VectorStoreService

def build_qa_planner_graph(vector_service: VectorStoreService):
    """
    Builds and compiles the Agentic QA Planner LangGraph workflow.
    """
    # Initialize the graph with the QAState schema
    builder = StateGraph(QAState)
    
    # Wrap retrieve_qa_docs to inject the vector_service dependency
    retrieve_node = functools.partial(retrieve_qa_docs, vector_service=vector_service)
    
    # Add nodes to the graph
    builder.add_node("retrieve_qa_docs", retrieve_node)
    builder.add_node("analyze_requirement", analyze_requirement)
    builder.add_node("generate_test_cases", generate_test_cases)
    builder.add_node("validate_tests", validate_tests)
    
    # Define the execution edges (linear sequence)
    builder.add_edge(START, "retrieve_qa_docs")
    builder.add_edge("retrieve_qa_docs", "analyze_requirement")
    builder.add_edge("analyze_requirement", "generate_test_cases")
    builder.add_edge("generate_test_cases", "validate_tests")
    builder.add_edge("validate_tests", END)
    
    # Compile the graph
    return builder.compile()


