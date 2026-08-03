# Agent Usage & AI Documentation

This document outlines how artificial intelligence and LLM agents were utilized within the Agentic QA Planning Assistant.

## 🛠️ Tools Used
- **LangChain**: Used to orchestrate LLM calls and parse structured JSON outputs via `PydanticOutputParser`.
- **LangGraph**: Used to construct a stateful, cyclic/acyclic graph architecture that handles the workflow (Retrieve -> Analyze -> Generate -> Validate).
- **FAISS**: Used as a local, in-memory vector database to embed and retrieve QA standard guidelines.
- **OpenAI (`gpt-4o` or similar)**: The core LLM powering the intelligence of the planner.

---

## 🤖 Work Delegated to Agents

The AI is delegated the creative and analytical heavy lifting, specifically:
1. **Context Retrieval**: Finding relevant QA guidelines based on semantic similarity to the user story.
2. **Analysis**: Extracting main user flows, identifying unspoken assumptions, and highlighting potential risks/edge cases.
3. **Test Generation**: Writing detailed, step-by-step test cases, mapping them to specific categories (e.g. Failure State, Happy Path) and explicitly mapping them to the provided Acceptance Criteria.

### What is *NOT* delegated to the Agent?
- **Coverage Math**: The calculation of coverage percentages and identification of uncovered ACs is handled by strict deterministic Python logic in `CoverageService`, not the LLM.
- **Approval**: The LLM cannot mark a plan as "Approved." All tests default to "Proposed" and require human intervention.

---

## 📝 Representative Prompts

**1. Requirement Analysis Prompt (`analyze.py`)**
> *"You are a Senior QA Architect. Review the following User Story and Implementation Summary. Use the provided QA Guidelines to inform your analysis. Identify the main user flows, unspoken assumptions, and potential risks/edge cases."*

**2. Test Case Generation Prompt (`generate.py`)**
> *"You are an elite Software Engineer in Test (SDET). Generate a comprehensive suite of test cases based on the analyzed requirements. Ensure you cover Unit, API, Integration, E2E, and Manual testing where appropriate. You MUST map each test case to at least one provided Acceptance Criteria ID. You must provide a clear rationale for why this test is necessary."*

---

## ⚠️ Important Agent Mistakes & Rejected Suggestions

During development and testing, several LLM hallucinations and mistakes were identified and handled:

1. **LLM doing Math**: Initially, the LLM was asked to estimate coverage percentage. It would frequently hallucinate a number like "80%" when it was actually 60%. 
   - **Correction**: We stripped all math responsibilities from the agent and implemented a deterministic `CoverageService` in Python.
2. **Invalid Enum Types**: The LLM would occasionally generate categories like `FRONTEND_TEST` instead of the strict Pydantic enums `HAPPY_PATH`, `EDGE_CASE`, etc.
   - **Correction**: We implemented strict output parsers with `PydanticOutputParser` and robust fallback `try/except` mapping logic in `planner_service.py` to default to `MANUAL` / `HAPPY_PATH` if the LLM hallucinated a category.
3. **Missing Steps**: The LLM would sometimes generate a test title but leave the `steps` array empty.
   - **Correction**: We added a `validate_tests` node in LangGraph to explicitly scan the output and flag these tests as `is_incomplete`.

---

## ✅ How Output Was Verified

The AI's generated output was verified through a multi-layered approach:

1. **Schema Enforcement**: LangChain's `PydanticOutputParser` guarantees the structural integrity of the JSON (e.g. ensuring `steps` is always a List of Strings).
2. **Graph Validation Node**: A secondary LangGraph node scans the output for human-readable quality (e.g., ensuring `rationale` is > 5 characters, checking for missing actionable steps).
3. **Deterministic Verification Services**: 
    - `DuplicateService.detect_duplicates()`: Uses `difflib.SequenceMatcher` to flag AI-generated tests that are essentially duplicates of one another.
    - `ValidationService.flag_incomplete_tests()`: A final programmatic check before saving to the DB to flag tests requiring human attention.
4. **Human in the Loop**: The ultimate verification is the React UI itself. The AI is restricted to proposing tests; a human operator must review the `flag_reason` warnings, manually edit the tests, and explicitly click "Approve" on each one.
