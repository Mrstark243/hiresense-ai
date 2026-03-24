# HireSense AI - Resume Intelligence System

HireSense AI is a full-stack, AI-powered recruitment tool that uses **Retrieval-Augmented Generation (RAG)** to analyze resumes against job descriptions. It provides recruiter-level insights, scoring, and multi-candidate ranking.

## 🚀 Key Features

*   **Semantic Matching**: Uses `sentence-transformers` to find conceptual matches beyond keywords.
*   **Explainable AI**: Provides detailed reasoning for why a candidate is or isn't a good fit.
*   **Skill Gap Analysis**: Identifies missing skills and suggests improvements.
*   **Multi-Candidate Ranking**: Upload multiple resumes to see a ranked leaderboard.
*   **Premium UI**: Fully responsive, dark-mode, glassmorphic design.

## 🛠️ Tech Stack

### Backend
*   **FastAPI**: High-performance Python framework.
*   **Sentence Transformers**: `all-MiniLM-L6-v2` for semantic search.
*   **FAISS**: Vector database for efficient retrieval.
*   **PyMuPDF**: Robust PDF parsing.

### Frontend
*   **React (Vite)**: Modern frontend development.
*   **Tailwind CSS**: Premium design system.
*   **Framer Motion**: Smooth animations.
*   **Recharts**: Data visualization.

## 🏃 Run the Project

### Prerequisites
*   Python 3.10+
*   Node.js 18+

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```
The backend will run at `http://localhost:8080`.

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The frontend will run at `http://localhost:5173`.

## 📂 Folder Structure

*   `backend/app/`: Core logic, routes, and services.
*   `frontend/src/`: React components, pages, and UI logic.
*   `artifacts/`: Project planning and documentation.

---

> [!TIP]
> This system uses a local rule-based reasoning engine powered by semantic search. No OpenAI API key is required.
