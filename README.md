# Agentic QA Planning Assistant

An AI-driven QA Planning Assistant built with FastAPI, LangGraph, React, and PostgreSQL. It allows developers to input a user story and acceptance criteria, and deterministically generates a comprehensive QA plan containing unit, API, integration, E2E, and manual test cases. 

The AI uses a Retrieval-Augmented Generation (RAG) architecture powered by Qdrant to ground its testing strategies in your provided QA markdown guidelines.

---

## 🏗️ Architecture

The application is built on a modern, decoupled architecture:

### Backend
- **Framework**: FastAPI (Python 3.12+)
- **AI Orchestration**: LangGraph (Stateful graph executing Retrieve -> Analyze -> Generate -> Validate)
- **Vector Store**: Qdrant Cloud (Managed vector database for RAG)
- **LLM Provider**: LangChain w/ OpenAI
- **Database**: PostgreSQL (via asyncpg and SQLAlchemy ORM)
- **Schema Validation**: Pydantic v2

### Frontend
- **Framework**: React 18 + Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS (Dark theme with custom Indigo/Purple aesthetics)
- **Routing**: React Router DOM
- **HTTP Client**: Axios

### AI Workflow (LangGraph)
1. **Retrieve**: Searches Qdrant Cloud index for relevant QA Markdown guidelines based on the user story.
2. **Analyze**: AI identifies main user flows, assumptions, and edge case risks.
3. **Generate**: AI proposes structured test cases (Happy Path, Edge Case, Failure State, etc.) with rationales.
4. **Validate**: Python logically flags missing rationales or steps.
5. **Coverage Calculation**: Strict, non-AI deterministic set logic compares the total generated AC coverage against the user's provided AC list.

---

## 🚀 Setup Instructions

### Prerequisites
- Node.js (v18+)
- Python (3.12+)
- PostgreSQL database
- OpenAI API Key

### 1. Database Setup
Ensure you have a PostgreSQL database running. Create a new database (e.g., `agentic_qa`).

### 2. Backend Setup
1. Navigate to the `backend` directory.
2. Create a virtual environment: `python -m venv .venv`
3. Activate it: `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in your `DATABASE_URL` and `OPENAI_API_KEY`.
6. Run database migrations: `alembic upgrade head`
7. Start the server: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`

### 3. Frontend Setup
1. Navigate to the `frontend` directory.
2. Install dependencies: `npm install`
3. Copy the frontend `.env.example` settings into a `.env` file (e.g. `VITE_API_BASE_URL="http://localhost:8000"`).
4. Start the Vite dev server: `npm run dev`

---

## 🎯 Completed Scope

- **RAG Implementation**: Qdrant Cloud vector store that automatically chunks and embeds `backend/qa_docs/` markdown files.
- **Agentic Workflow**: LangGraph pipeline with Retrieve, Analyze, Generate, and Validate nodes.
- **Deterministic Coverage**: Accurate math-based calculation of coverage % and explicit highlighting of missed Acceptance Criteria.
- **Test Generation**: Generates categorised tests (Unit, API, Manual, E2E) mapped strictly to ACs.
- **Interactive UI**: A fully responsive, dark-mode React application allowing inline edits, approvals, rejections, and test reprioritization.
- **Version Control**: Ability to snapshot approved/rejected states of the plan over time via the "Create Snapshot" feature.
- **Duplicate & Incomplete Flagging**: AI-flagged tests emit visually distinct warnings in the UI.

## 🚫 Intentionally Excluded Scope

- **Execution of Tests**: The AI proposes tests; it *does not* run them. This is strictly a planning and documentation assistant.
- **Authentication/Authorization**: The app currently operates in a single-tenant/local mode without JWT user login.
- **Real-Time WebSockets**: Graph execution logs are currently fetched synchronously. Streaming node-by-node updates via WebSockets was excluded for simplicity.

---

## 🧪 Tests

Currently, the system is tested via a comprehensive integration script rather than a standard `pytest` suite:
- `backend/scripts/test_graph.py`: Executes the full LangGraph pipeline from start to finish outside of the FastAPI context, verifying DB commits, schema validation, and vector store retrieval.

To run the integration script:
```bash
cd backend
python -m scripts.test_graph
```

---

## ⚠️ Known Limitations

1. **Cold Start Penalty**: On the very first launch, the vector store must parse and embed all local markdown docs via OpenAI and push to Qdrant, causing the first startup to take several extra seconds. 
2. **Context Window Limitations**: Extremely large implementation summaries could exceed the standard LLM context window during the `generate` node.
3. **No Auto-Fixing Graph**: The current LangGraph is linear. While it validates tests and generates errors, it does not currently loop back to self-correct the tests (reflection). It simply surfaces those errors to the human operator.

---

## 📦 Deployment Details

- **Backend**: Suitable for deployment on platforms like Render, Railway, or AWS Elastic Beanstalk using Gunicorn with Uvicorn workers. Ensure your QDRANT_URL and API keys are set.
- **Frontend**: Standard Vite static site. Can be deployed to Vercel, Netlify, or AWS S3. Ensure `VITE_API_BASE_URL` is set to the production backend URL during the build step.
- **Database**: Any managed PostgreSQL provider (e.g., Neon, Supabase, AWS RDS).
