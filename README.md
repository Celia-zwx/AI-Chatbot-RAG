# 🤖 AI-Chatbot-RAG

**AI-Chatbot-RAG** is a locally hosted, Retrieval-Augmented Generation (RAG) chatbot designed for answering questions based on your own documents.  
Built with [LangChain](https://github.com/langchain-ai/langchain/), [FastAPI](https://fastapi.tiangolo.com/), and [Next.js](https://nextjs.org/), this system supports streaming responses, real-time interaction, and flexible ingestion.

---

## ✅ Running Locally

1. **Install backend dependencies:**
   ```bash
   poetry install
   ```

2. **Set environment variables:**
   ```bash
   export OPENAI_API_KEY=
   export WEAVIATE_URL=
   export WEAVIATE_API_KEY=
   export RECORD_MANAGER_DB_URL=

   # optional tracing (LangSmith)
   export LANGCHAIN_TRACING_V2=true
   export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
   export LANGCHAIN_API_KEY=
   export LANGCHAIN_PROJECT=
   ```

3. **Add your documents:**
   - Place all your PDF files inside the `./data/pdfs/` folder.
   - These will be processed and indexed into the vector database.

4. **Run the ingestion script (only once):**
   ```bash
   python backend/ingest.py
   ```

5. **Start the backend server:**
   ```bash
   make start
   ```

6. **Install frontend dependencies:**
   ```bash
   cd ./frontend
   yarn
   ```

7. **Start the frontend:**
   ```bash
   yarn dev
   ```

8. **Open in browser:**
   Visit [http://localhost:3000](http://localhost:3000)

---

## 📚 Technical Overview

### 🔄 Ingestion Pipeline

- Load PDF files from `./data/pdfs/` using LangChain's `PyPDFLoader`.
- Split content with `RecursiveCharacterTextSplitter`.
- Generate embeddings with OpenAI's API.
- Store embeddings in a Weaviate vectorstore.

### 💬 Question Answering Flow

1. Convert user input and chat history into a standalone query.
2. Retrieve relevant document chunks from the vectorstore.
3. Use retrieved documents + standalone query to generate a response via OpenAI.
4. Stream the final answer back to the frontend.
5. Optionally, collect feedback and tracing via LangSmith.

---

## 📄 Documentation

- **[CONCEPTS.md](./CONCEPTS.md)** – System architecture and feature explanation.
- **[MODIFY.md](./MODIFY.md)** – How to customize the system to your use case.
- **[RUN_LOCALLY.md](./RUN_LOCALLY.md)** – A standalone version of this setup guide.
- **[LANGSMITH.md](./LANGSMITH.md)** – Enabling traceability, evaluation, and feedback.
- **[PRODUCTION.md](./PRODUCTION.md)** – Hardening your deployment for production.
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** – Frontend/backend deployment instructions.

---
