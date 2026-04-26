# College Admission Assistant

This is a full-stack AI-powered College Admission Assistant. It leverages a Retrieval-Augmented Generation (RAG) pipeline to query an internal dataset (CSV) and an Agentic framework (LangChain) to dynamically fetch real-time official data from the US Department of Education's College Scorecard API.

## Architecture Overview

- **Frontend:** React (Vite) with a modern, glassmorphism-styled chat interface built using Vanilla CSS.
- **Backend:** FastAPI (Python) for robust, high-performance API endpoints.
- **AI Core:** LangChain, utilizing **Ollama (`qwen2.5:3b`)** for reasoning to guarantee 100% free, unlimited, and private local inference.
- **Vector Store:** **ChromaDB** with `nomic-embed-text` embeddings for persistent RAG storage.

---

## Prerequisites

- **Python:** 3.10 or higher.
- **Node.js:** v18 or higher.
- **Ollama:** Installed locally (download from [ollama.com](https://ollama.com/)).
- **API Keys:**
  1. Data.gov API Key (for the College Scorecard API)

---

## Setup & Running Instructions

### 1. Download Local AI Models

Before starting the backend, make sure Ollama is running on your machine and pull the required models by running these commands in your terminal:
```bash
ollama pull qwen2.5:3b
ollama pull nomic-embed-text
```

### 2. Environment Variables Configuration

1. Navigate to the `backend/` directory.
2. Open the `.env` file and insert your Data.gov API key:
   ```env
   DATAGOV_API_KEY="your_actual_datagov_key_here"
   ```

### 3. Run the Backend (FastAPI)

1. Open a terminal and navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```
3. Install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the backend server:
   ```bash
   python main.py
   ```
   *The backend will start on `http://localhost:8000` and will automatically load your CSV into the `chroma_db` folder using Ollama.*

### 4. Run the Frontend (React / Vite)

1. Open a **new, separate terminal** and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install the Node modules:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser and go to the link provided by Vite (usually `http://localhost:5173`).

---

## Usage Instructions

- Once both servers are running, type your college admission queries into the frontend chat interface. 
- You can ask about data present in your CSV file (e.g., eligibility, required documents for specific courses).
- You can also ask for real-time data like: *"What is the acceptance rate at Stanford University?"* and the Agent will dynamically route your query to the College Scorecard API.
