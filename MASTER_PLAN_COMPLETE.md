# AI/LLM Engineer Master Plan - Complete 10-Week Guide

**CRITICAL:** This document contains the COMPLETE learning plan. Claude Code should use this to guide the user through ALL 10 weeks without needing to reference external sources.

**User:** Jigar, Senior Java Backend Engineer (8+ years) → AI/LLM Engineer  
**Timeline:** 10 weeks, 15-25 hours/week  
**Goal:** Portfolio-ready projects + interview readiness + production AI skills

---

## 📊 COMPLETE PROGRAM STRUCTURE

### Overview
```
Week 1-2:   Project 1 - Intelligent Task Router (Hybrid AI/Classical)
Week 3-5:   Project 2 - Big-O Code Reviewer (LangChain Agents) - MVP ONLY
Week 6-8:   Project 3 - High-Performance RAG System (PostgreSQL + pgvector) - FULL SHIP
Week 9-10:  Portfolio polish, interview prep, case studies
```

### Philosophy
- **Week 1-2:** Deep implementation (one polished project)
- **Week 3-5:** Breadth (MVP to learn new concepts)
- **Week 6-8:** Full production system (flagship project)
- **Week 9-10:** Portfolio + interviews

---

## ✅ WEEKS 1-2: INTELLIGENT TASK ROUTER (COMPLETED/IN PROGRESS)

**Status:** Week 1 COMPLETE, Week 2 IN PROGRESS  
**Location:** `~/ai-llm-engineer/project1-task-router/`

See CLAUDE_CODE_HANDOFF.md for complete Week 1-2 details.

**Key Achievement:** Hybrid AI/Classical routing with 70% cost savings

---

## 🚀 WEEKS 3-5: BIG-O CODE REVIEWER (MVP ONLY)

**Goal:** Learn LangChain, AI agents, tool use - NOT to build a perfect product

**Location:** `~/ai-llm-engineer/project2-code-reviewer/`

### Concept

An AI agent that analyzes code from GitHub PRs, identifies time/space complexity issues, and suggests optimizations.

**Why This Project:**
- Learn **LangChain** framework
- Understand **AI agents** and tool use
- Practice **streaming responses**
- Learn **GitHub API** integration
- Focus on algorithmic thinking (your strength!)

**Scope:** MVP only - working prototype to demonstrate concepts

---

### Technical Stack

**Core:**
- **Language:** Python 3.11+
- **LLM:** Google Gemini 3 Flash Preview (consistent with Project 1)
- **Framework:** LangChain 0.1.x
- **GitHub:** PyGithub library
- **API:** FastAPI (consistent with Project 1)

**New Concepts You'll Learn:**
1. **LangChain Basics**
   - Chains (sequential, routing)
   - Agents (ReAct pattern)
   - Tools (function calling)
   - Memory (conversation history)

2. **Streaming Responses**
   - Token-by-token output
   - Server-Sent Events (SSE)
   - User experience for slow LLM calls

3. **Tool Use / Function Calling**
   - Define tools for LLM
   - Execute tool calls
   - Chain multiple tools

---

### Learning Resources (Week 3)

**Before coding, complete these:**

1. **LangChain for LLM Application Development** (DeepLearning.AI)
   - URL: https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/
   - Time: 1 hour
   - Focus: Chains, agents, tools

2. **Read LangChain Docs**
   - Agents: https://python.langchain.com/docs/modules/agents/
   - Tools: https://python.langchain.com/docs/modules/tools/
   - Chains: https://python.langchain.com/docs/modules/chains/
   - Time: 2-3 hours (skim, don't read everything)

3. **GitHub API Exploration**
   - Test PyGithub library
   - Fetch PR data, file diffs
   - Time: 1 hour

**Total Learning Time:** 4-5 hours

---

### Project Architecture

```
User → FastAPI → LangChain Agent → [Tools] → Response
                                      ↓
                                  - fetch_pr (GitHub API)
                                  - analyze_complexity (LLM)
                                  - suggest_optimization (LLM)
```

**Flow:**
1. User provides GitHub PR URL
2. Agent uses `fetch_pr` tool to get code changes
3. Agent uses `analyze_complexity` to identify O(n²) patterns
4. Agent uses `suggest_optimization` to propose improvements
5. Stream response back to user

---

### Week-by-Week Breakdown

#### **Week 3: Learning + Basic Setup (10-15 hours)**

**Monday-Tuesday (4-5 hours):**
- Complete LangChain course
- Read essential docs
- Install dependencies

**Wednesday-Thursday (3-4 hours):**
- Project structure setup
- GitHub API exploration
- Test fetching PR data

**Friday (3 hours):**
- First LangChain agent
- Simple tool definition
- Basic chain execution

**Weekend (0-3 hours):**
- Buffer time
- Experiment with examples

**Deliverables:**
- [ ] LangChain course completed
- [ ] Basic project structure
- [ ] Can fetch PR from GitHub
- [ ] Simple agent responds to queries

---

#### **Week 4: Core Implementation (12-18 hours)**

**Monday-Tuesday (6-8 hours):**
- Build complexity analysis tool
- Pattern detection (nested loops, etc.)
- LLM-based analysis chain

**Wednesday-Thursday (4-6 hours):**
- Build optimization suggestion tool
- Context-aware suggestions
- Code example generation

**Friday-Saturday (2-4 hours):**
- Agent integration
- Chain tools together
- Test end-to-end flow

**Deliverables:**
- [ ] Can analyze code complexity
- [ ] Can suggest optimizations
- [ ] Agent chains tools correctly
- [ ] Basic FastAPI endpoint works

---

#### **Week 5: Polish to MVP (8-12 hours)**

**Monday-Tuesday (4-6 hours):**
- Streaming response implementation
- Better error handling
- Input validation

**Wednesday-Thursday (2-3 hours):**
- Basic README
- Usage examples
- Quick demo

**Friday (2-3 hours):**
- Final testing
- Screenshots
- Move to next project

**Deliverables:**
- [ ] Working MVP demo
- [ ] Can analyze real GitHub PRs
- [ ] Streaming works
- [ ] Basic documentation
- [ ] **STOP HERE - MVP complete**

---

### Files to Create (Week 3-5)

```
project2-code-reviewer/
├── models.py               # Pydantic schemas
├── config.py               # Configuration
├── tools/
│   ├── github_tool.py      # Fetch PR data
│   ├── complexity_tool.py  # Analyze complexity
│   └── optimize_tool.py    # Suggest optimizations
├── agent.py                # LangChain agent setup
├── main.py                 # FastAPI application
├── requirements.txt        # Dependencies
├── .env                    # API keys
└── README.md               # Basic usage guide
```

---

### Core Code Patterns (Week 4)

#### 1. Tool Definition (LangChain Pattern)

```python
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI

# Define a tool
def fetch_pr_changes(pr_url: str) -> str:
    """Fetch code changes from GitHub PR"""
    # Use PyGithub to fetch PR
    # Return file diffs as string
    pass

github_tool = Tool(
    name="fetch_pr",
    func=fetch_pr_changes,
    description="Fetches code changes from a GitHub pull request URL"
)

# Create LLM
llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")

# Create agent with tools
agent = create_react_agent(
    llm=llm,
    tools=[github_tool],
    prompt=agent_prompt_template
)

# Execute
agent_executor = AgentExecutor(agent=agent, tools=[github_tool])
result = agent_executor.invoke({"input": "Analyze PR https://..."})
```

#### 2. Streaming Response Pattern

```python
from fastapi.responses import StreamingResponse

async def stream_analysis(pr_url: str):
    """Stream analysis results token by token"""
    for chunk in agent_executor.stream({"input": pr_url}):
        if "output" in chunk:
            yield f"data: {chunk['output']}\n\n"

@app.get("/analyze")
async def analyze_pr(pr_url: str):
    return StreamingResponse(
        stream_analysis(pr_url),
        media_type="text/event-stream"
    )
```

#### 3. Complexity Analysis Tool

```python
def analyze_complexity(code: str) -> dict:
    """
    Analyze time/space complexity of code.
    Use LLM with specific prompt for analysis.
    """
    prompt = f"""
    Analyze the time and space complexity of this code:
    
    {code}
    
    Return JSON:
    {{
        "time_complexity": "O(...)",
        "space_complexity": "O(...)",
        "bottlenecks": ["line X: nested loop", ...],
        "reasoning": "..."
    }}
    """
    
    response = llm.invoke(prompt)
    return json.loads(response.content)
```

---

### Success Criteria (MVP)

Project 2 is **MVP complete** when:

- [ ] Can fetch PR data from GitHub URL
- [ ] Identifies common complexity issues (nested loops, etc.)
- [ ] Suggests one optimization (doesn't need to be perfect)
- [ ] Streams response to user
- [ ] Has basic FastAPI endpoint
- [ ] Has README with example usage
- [ ] Takes <20 hours total (stop if taking longer)

**NOT required for MVP:**
- ❌ Perfect complexity analysis
- ❌ Multiple optimization strategies
- ❌ Production error handling
- ❌ Docker deployment
- ❌ Comprehensive testing
- ❌ Beautiful UI

**Interview value:** "Built LangChain agent with GitHub integration, learned tool use and streaming"

---

## 🎯 WEEKS 6-8: HIGH-PERFORMANCE RAG SYSTEM (FULL PRODUCTION)

**Goal:** Build a COMPLETE, production-ready RAG system - this is your flagship project

**Location:** `~/ai-llm-engineer/project3-rag-system/`

### Concept

A semantic search system that ingests documents, chunks them, embeds them, stores in PostgreSQL with pgvector, and retrieves relevant context for question-answering.

**Why This Project:**
- RAG is **the most common** production LLM pattern
- Learn **vector databases** (critical skill)
- **Full production system** (unlike Project 2 MVP)
- Database expertise (your strength!) applied to AI
- Portfolio centerpiece

**Scope:** Full production - Docker, monitoring, documentation, performance optimization

---

### Technical Stack

**Core:**
- **Language:** Python 3.11+
- **LLM:** Google Gemini 3 Flash Preview
- **Vector DB:** PostgreSQL 15+ with pgvector extension
- **Framework:** LangChain 0.1.x
- **API:** FastAPI
- **Embeddings:** Google text-embedding-004 (free tier)

**Infrastructure:**
- **Docker Compose:** Postgres + App
- **Logging:** Structured JSON logs
- **Monitoring:** Prometheus metrics (optional)
- **Testing:** pytest with real DB tests

**New Concepts You'll Learn:**
1. **Vector Embeddings**
   - Text → vector representation
   - Semantic similarity
   - Embedding models

2. **Vector Databases**
   - pgvector extension
   - Similarity search (cosine, L2)
   - Index optimization (HNSW, IVFFlat)

3. **RAG Pipeline**
   - Document ingestion
   - Chunking strategies
   - Retrieval + generation
   - Context window management

4. **Production PostgreSQL**
   - Connection pooling
   - Query optimization
   - Index tuning
   - Monitoring

---

### Learning Resources (Week 6)

**Before coding, complete these:**

1. **LangChain: Chat with Your Data** (DeepLearning.AI)
   - URL: https://www.deeplearning.ai/short-courses/langchain-chat-with-your-data/
   - Time: 1 hour
   - Focus: Document loaders, text splitting, retrieval

2. **pgvector Documentation**
   - URL: https://github.com/pgvector/pgvector
   - Focus: Installation, indexing, similarity search
   - Time: 1 hour

3. **Vector Embeddings Concepts**
   - Read: https://www.pinecone.io/learn/vector-embeddings/
   - Understand: semantic similarity, cosine distance
   - Time: 30 minutes

4. **RAG Pattern Deep Dive**
   - Read LangChain RAG docs
   - Understand: retrieval strategies, context management
   - Time: 1-2 hours

**Total Learning Time:** 4-5 hours

---

### Project Architecture

```
Documents → Chunking → Embedding → PostgreSQL (pgvector)
                                         ↓
User Query → Embedding → Similarity Search → Top K chunks
                                               ↓
                                          Context + Query → LLM → Answer
```

**Key Components:**

1. **Ingestion Pipeline**
   - Document upload (PDF, TXT, MD)
   - Text extraction
   - Chunking (semantic, fixed-size, recursive)
   - Embedding generation
   - Vector storage

2. **Retrieval System**
   - Query embedding
   - Similarity search (cosine distance)
   - Top-K retrieval
   - Re-ranking (optional)

3. **Generation System**
   - Context assembly
   - Prompt construction
   - LLM generation
   - Source citation

4. **API Layer**
   - Document upload endpoint
   - Query endpoint
   - Document management
   - Health checks

---

### Week-by-Week Breakdown

#### **Week 6: Learning + Infrastructure (12-18 hours)**

**Monday-Tuesday (5-7 hours):**
- Complete "Chat with Your Data" course
- Read pgvector docs
- Understand RAG pattern

**Wednesday-Thursday (4-6 hours):**
- Setup PostgreSQL + pgvector in Docker
- Test vector operations manually
- Create database schema

**Friday (3 hours):**
- Project structure
- Basic document loader
- Test embedding API

**Weekend (0-4 hours):**
- Experiment with chunking
- Test retrieval queries

**Deliverables:**
- [ ] Course completed
- [ ] PostgreSQL + pgvector running
- [ ] Can store/query vectors
- [ ] Basic project structure
- [ ] Understanding of RAG flow

---

#### **Week 7: Core RAG Implementation (15-20 hours)**

**Monday-Tuesday (6-8 hours):**
- Document ingestion pipeline
  - File upload handling
  - Text extraction (PDF, TXT)
  - Chunking strategies
  - Embedding generation
  - Database storage

**Wednesday-Thursday (6-8 hours):**
- Retrieval system
  - Query processing
  - Similarity search
  - Context assembly
  - LLM generation
  - Response formatting

**Friday (3-4 hours):**
- FastAPI endpoints
  - POST /upload (ingest document)
  - POST /query (ask question)
  - GET /documents (list documents)
  - DELETE /documents/{id}

**Deliverables:**
- [ ] Can upload and chunk documents
- [ ] Can query and get relevant answers
- [ ] Citations to source chunks
- [ ] API endpoints work
- [ ] End-to-end RAG flow complete

---

#### **Week 8: Production Polish (12-18 hours)**

**Monday-Tuesday (5-7 hours):**
- Performance optimization
  - pgvector indexing (HNSW)
  - Connection pooling
  - Query optimization
  - Chunking strategy tuning

**Wednesday-Thursday (4-6 hours):**
- Production features
  - Structured logging
  - Error handling
  - Input validation
  - Rate limiting

**Friday-Saturday (3-5 hours):**
- Docker Compose production setup
  - Multi-container orchestration
  - Environment configuration
  - Volume persistence
  - Health checks

**Sunday (0-2 hours):**
- Testing
  - Integration tests
  - Performance benchmarks
  - Load testing

**Deliverables:**
- [ ] Optimized performance (p95 < 2s)
- [ ] Production logging
- [ ] Docker Compose deployment
- [ ] Tests passing
- [ ] Error handling comprehensive

---

### Week 8 (Continued): Documentation & Polish (6-10 hours)

**After core implementation:**

1. **Professional README (3-4 hours)**
   - Architecture diagram
   - Setup instructions
   - API documentation
   - Performance benchmarks
   - Deployment guide

2. **Performance Documentation (2-3 hours)**
   - Query latency analysis
   - Chunking strategy comparison
   - Index performance comparison
   - Cost analysis (embeddings, LLM)

3. **Code Quality (1-2 hours)**
   - Linting (black, pylint)
   - Type hints
   - Docstrings
   - Code cleanup

4. **Portfolio Assets (1 hour)**
   - Screenshots of API docs
   - Query examples with results
   - Performance graphs
   - Architecture diagrams

---

### Files to Create (Week 6-8)

```
project3-rag-system/
├── models.py               # Pydantic schemas
├── config.py               # Configuration
├── database/
│   ├── connection.py       # PostgreSQL connection pool
│   ├── schema.sql          # Database schema + pgvector
│   └── queries.py          # SQL queries
├── ingestion/
│   ├── loader.py           # Document loading
│   ├── chunker.py          # Text chunking
│   └── embedder.py         # Embedding generation
├── retrieval/
│   ├── search.py           # Similarity search
│   └── reranker.py         # Optional re-ranking
├── generation/
│   ├── prompt.py           # Prompt templates
│   └── generator.py        # LLM generation
├── main.py                 # FastAPI application
├── requirements.txt        # Dependencies
├── docker-compose.yml      # PostgreSQL + App
├── Dockerfile              # Application container
├── .env                    # Configuration
├── tests/
│   ├── test_ingestion.py
│   ├── test_retrieval.py
│   └── test_integration.py
└── README.md               # Complete documentation
```

---

### Core Code Patterns (Week 7)

#### 1. Database Schema (pgvector)

```sql
-- schema.sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    embedding vector(768),  -- Google text-embedding-004 dimension
    chunk_index INTEGER NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for similarity search (HNSW for speed)
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);
```

#### 2. Chunking Strategy

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_document(text: str, chunk_size: int = 1000, overlap: int = 200):
    """
    Chunk document using recursive strategy.
    Tries to split on paragraphs, then sentences, then characters.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = splitter.split_text(text)
    return chunks
```

#### 3. Embedding Generation

```python
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004"
)

def embed_chunks(chunks: list[str]) -> list[list[float]]:
    """Generate embeddings for text chunks"""
    return embeddings.embed_documents(chunks)

def embed_query(query: str) -> list[float]:
    """Generate embedding for search query"""
    return embeddings.embed_query(query)
```

#### 4. Similarity Search

```python
import psycopg2
from pgvector.psycopg2 import register_vector

def similarity_search(query_embedding: list[float], top_k: int = 5):
    """
    Search for most similar chunks using cosine similarity.
    Returns: list of (chunk_id, content, distance)
    """
    conn = get_db_connection()
    register_vector(conn)
    cursor = conn.cursor()
    
    cursor.execute(
        """
        SELECT id, content, embedding <=> %s::vector AS distance
        FROM chunks
        ORDER BY distance
        LIMIT %s
        """,
        (query_embedding, top_k)
    )
    
    results = cursor.fetchall()
    cursor.close()
    return results
```

#### 5. RAG Chain

```python
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI

def create_rag_chain(retriever):
    """Create RAG chain for question answering"""
    llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview")
    
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # Simple: stuff all context into prompt
        retriever=retriever,
        return_source_documents=True
    )
    
    return chain

# Usage:
result = chain.invoke({"query": "What is the main topic?"})
answer = result["result"]
sources = result["source_documents"]
```

---

### Performance Optimization (Week 8)

#### 1. pgvector Index Types

```sql
-- IVFFlat (faster build, slower search)
CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- HNSW (slower build, faster search) - RECOMMENDED
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);
```

**Benchmarking:**
- Test with 10K, 50K, 100K chunks
- Measure query latency
- Choose based on dataset size

#### 2. Connection Pooling

```python
from psycopg2.pool import ThreadedConnectionPool

pool = ThreadedConnectionPool(
    minconn=2,
    maxconn=10,
    host="localhost",
    database="rag_db",
    user="postgres",
    password="password"
)

def get_db_connection():
    """Get connection from pool"""
    return pool.getconn()

def release_db_connection(conn):
    """Return connection to pool"""
    pool.putconn(conn)
```

#### 3. Batch Embedding

```python
def embed_chunks_batch(chunks: list[str], batch_size: int = 100):
    """
    Embed chunks in batches to reduce API calls.
    Google allows up to 2048 inputs per request.
    """
    embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        batch_embeddings = embeddings_model.embed_documents(batch)
        embeddings.extend(batch_embeddings)
    return embeddings
```

---

### Success Criteria (Full Production)

Project 3 is **complete** when:

**Core Functionality:**
- [ ] Can upload documents (PDF, TXT, MD)
- [ ] Chunks documents intelligently
- [ ] Generates embeddings and stores in PostgreSQL
- [ ] Retrieves relevant context for queries
- [ ] Generates accurate answers with source citations
- [ ] API endpoints all working

**Performance:**
- [ ] Query latency p95 < 2 seconds
- [ ] Can handle 10K+ chunks
- [ ] pgvector index optimized
- [ ] Connection pooling implemented

**Production Features:**
- [ ] Docker Compose deployment
- [ ] Structured logging
- [ ] Comprehensive error handling
- [ ] Input validation
- [ ] Health checks

**Documentation:**
- [ ] Professional README with architecture
- [ ] API documentation
- [ ] Setup/deployment guide
- [ ] Performance benchmarks
- [ ] Code is well-commented

**Testing:**
- [ ] Integration tests passing
- [ ] Performance benchmarks run
- [ ] Manual testing complete

**Portfolio:**
- [ ] Screenshots taken
- [ ] Example queries documented
- [ ] Architecture diagram created

---

## 🎓 WEEKS 9-10: PORTFOLIO POLISH & INTERVIEW PREP

**Goal:** Convert projects into interview-ready portfolio + prepare talking points

---

### Week 9: Portfolio & Documentation (10-15 hours)

**Monday-Tuesday (4-6 hours):**

**1. Project Summaries (2 hours)**

Create 1-page summary for each project:
- Problem statement
- Technical approach
- Key decisions and trade-offs
- Performance metrics
- What you learned

**2. Master Portfolio README (2 hours)**

Create `~/ai-llm-engineer/README.md`:
- Overview of learning journey
- Links to all 3 projects
- Skills acquired
- Technologies used
- Quick-start for each project

**3. Architecture Diagrams (2 hours)**

Create clean diagrams for each project using:
- Mermaid (in markdown)
- Draw.io
- Excalidraw

---

**Wednesday-Thursday (4-6 hours):**

**4. Case Studies (3-4 hours)**

Write detailed case study for Project 3 (flagship):
- Business context
- Technical challenges
- Solution architecture
- Implementation decisions
- Performance optimization
- Results and metrics
- Future improvements

**5. Code Cleanup (1-2 hours)**
- Run linters on all projects
- Add missing docstrings
- Remove dead code
- Consistent formatting

---

**Friday (2-3 hours):**

**6. Demo Videos/Screenshots**
- Record quick demo of each project
- Take screenshots of key features
- Capture performance metrics
- API documentation screenshots

**7. GitHub Repository Setup**
- Push all projects to GitHub
- Professional README for each
- Add badges (Python, Docker, etc.)
- Add LICENSE files
- Pin best projects to profile

---

### Week 10: Interview Preparation (12-18 hours)

**Monday-Tuesday (6-8 hours):**

**1. Technical Talking Points (3-4 hours)**

For each project, prepare to explain:
- **30-second pitch** (elevator version)
- **2-minute technical deep dive**
- **5-minute architecture walkthrough**
- **Trade-offs and decisions**
- **What you'd do differently**

**Example Template:**
```
Project: Intelligent Task Router

30-Second Pitch:
"I built a hybrid AI/classical ticket routing system that achieves 
70% cost savings by using fast keyword matching first, only calling 
the expensive LLM when confidence is low. It maintains 87% accuracy 
while being 3x faster than a pure AI approach."

Technical Deep Dive:
"The system uses structured outputs with Pydantic validation, 
eliminating JSON parsing errors. I implemented two modes - 
classical-first for production cost optimization, and LLM-first 
for accuracy-critical scenarios. The architecture includes..."

Key Decisions:
"I chose classical-first as default because analysis showed 70% 
of tickets had clear keywords. The business impact is $6/month 
savings per 1000 tickets while maintaining quality..."
```

Create these for all 3 projects.

**2. Common Interview Questions (2-3 hours)**

Prepare answers to:

**AI/LLM Specific:**
- "When would you use AI vs traditional algorithms?"
- "How do you prevent hallucinations in production?"
- "Explain RAG and when to use it vs fine-tuning"
- "How do you evaluate LLM performance?"
- "Describe your approach to prompt engineering"
- "How do you handle LLM costs at scale?"

**System Design:**
- "Design a content moderation system using LLMs"
- "How would you build a chatbot for customer support?"
- "Design a code review system with AI"

**Your Projects:**
- "Walk me through your RAG system architecture"
- "How did you optimize query performance?"
- "What was the biggest challenge in Project X?"

---

**Wednesday-Thursday (4-6 hours):**

**3. Mock Interviews (2-3 hours)**
- Practice technical explanations
- Record yourself explaining projects
- Time your responses
- Refine based on recording

**4. Portfolio Website (2-3 hours)**
- Simple GitHub Pages site OR
- Update LinkedIn with project links
- Ensure all GitHub repos are polished

---

**Friday (2-4 hours):**

**5. Final Review**
- Validate all projects still run
- Test deployment instructions
- Fix any broken links/screenshots
- Ensure READMEs are accurate

**6. Job Application Strategy**
- Identify target companies
- Customize resume for AI roles
- Prepare cover letter template
- LinkedIn profile update

---

## 📊 COMPLETE SKILLS ACQUIRED

By end of 10 weeks, you'll have:

### **Technical Skills**

**LLM Integration:**
- ✅ Prompt engineering (temperature, few-shot, system prompts)
- ✅ Structured outputs with Pydantic
- ✅ Error handling and fallback strategies
- ✅ Cost optimization techniques
- ✅ Streaming responses

**LangChain:**
- ✅ Chains (sequential, routing)
- ✅ Agents (ReAct pattern)
- ✅ Tools and function calling
- ✅ Memory management
- ✅ Document loaders and text splitters

**Vector Databases:**
- ✅ pgvector with PostgreSQL
- ✅ Embedding generation
- ✅ Similarity search (cosine, L2)
- ✅ Index optimization (HNSW, IVFFlat)
- ✅ Query optimization

**Production Patterns:**
- ✅ Hybrid AI/classical systems
- ✅ Graceful degradation
- ✅ Structured logging
- ✅ Performance monitoring (p95/p99)
- ✅ Docker containerization
- ✅ API design with FastAPI

**RAG Systems:**
- ✅ Document ingestion pipelines
- ✅ Chunking strategies
- ✅ Retrieval optimization
- ✅ Context management
- ✅ Source citation

---

### **Portfolio Projects**

1. **Intelligent Task Router** (Production-ready)
   - Hybrid AI/classical routing
   - 70% cost savings
   - Dual-mode architecture
   - Complete documentation

2. **Big-O Code Reviewer** (MVP)
   - LangChain agent
   - GitHub integration
   - Tool use demonstration
   - Streaming responses

3. **High-Performance RAG System** (Flagship)
   - Full production system
   - PostgreSQL + pgvector
   - Optimized performance
   - Comprehensive documentation

---

## 💼 INTERVIEW POSITIONING

### **Your Unique Value Proposition**

"Senior backend engineer with 9 years of production experience, now adding AI/LLM capabilities. I understand when NOT to use AI - my projects demonstrate hybrid approaches that balance accuracy, cost, and reliability. I bring database optimization, system design, and production mindset to AI systems."

### **Key Differentiators**

1. **Production Focus**
   - Not just "AI everything"
   - Cost-conscious hybrid approaches
   - Graceful degradation and error handling

2. **Database Expertise + AI**
   - Deep PostgreSQL knowledge
   - pgvector optimization
   - Query performance tuning

3. **Backend Engineering Discipline**
   - Type safety (Pydantic)
   - Structured logging
   - Comprehensive testing
   - Docker deployment

4. **Business-Minded**
   - ROI calculations (70% cost savings)
   - Performance metrics (p95/p99)
   - Trade-off analysis

---

## 🎯 POST-COMPLETION OPTIONS

After completing the 10-week plan:

### **Option A: Deepen (Recommended if interviews are 2+ months away)**

**Advanced Projects:**
1. **Fine-tuning Project**
   - Fine-tune Gemini on custom dataset
   - Compare fine-tuned vs RAG vs prompting
   - Time: 2-3 weeks

2. **Multi-modal RAG**
   - Add image search to RAG system
   - Vision embeddings
   - Time: 1-2 weeks

3. **LLM Evaluation Framework**
   - Build automated evaluation system
   - Compare models/prompts
   - Time: 1-2 weeks

---

### **Option B: Broaden (If you want more variety)**

**Additional Mini-Projects:**
1. **Sentiment Analysis API** (1 week)
2. **Text Classification System** (1 week)
3. **Summarization Service** (1 week)

---

### **Option C: Specialize (Focus on one area)**

**Choose one:**
1. **RAG Expert** - Build 3 RAG variants
2. **Agent Specialist** - Build complex multi-agent systems
3. **Production AI** - Focus on deployment, monitoring, scaling

---

## 🚨 COMMON PITFALLS TO AVOID

### **During Learning:**

1. ❌ **Perfectionism on MVP projects**
   - Project 2 is MVP only - don't over-build
   - 20 hours max, then move on

2. ❌ **Skipping the courses**
   - Foundation courses save time later
   - Better understanding = faster coding

3. ❌ **Not testing incrementally**
   - Test each component as you build
   - Don't accumulate untested code

4. ❌ **Copying code without understanding**
   - Always understand WHY, not just WHAT
   - Explain it in your own words

5. ❌ **Ignoring cost optimization**
   - Always consider API costs
   - Implement caching, fallbacks

---

### **During Interviews:**

1. ❌ **Overstating capabilities**
   - Be honest: "I built 3 projects, still learning"
   - Emphasize: "I learn fast, production mindset"

2. ❌ **Ignoring trade-offs**
   - Always discuss: accuracy vs cost vs latency
   - Show engineering judgment

3. ❌ **Buzzword bingo**
   - Use natural language
   - Explain concepts clearly

4. ❌ **Not showing code**
   - GitHub links ready
   - Can walkthrough code live

---

## 📚 COMPLETE RESOURCE LIST

### **Courses (All Free)**

1. **Prompt Engineering** (Week 1)
   - https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/

2. **LangChain for LLM Applications** (Week 3)
   - https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/

3. **LangChain: Chat with Your Data** (Week 6)
   - https://www.deeplearning.ai/short-courses/langchain-chat-with-your-data/

### **Documentation**

1. **Google Gemini API**
   - https://ai.google.dev/docs
   - Focus: Structured outputs, function calling

2. **LangChain Python**
   - https://python.langchain.com/docs/
   - Focus: Agents, chains, tools, RAG

3. **pgvector**
   - https://github.com/pgvector/pgvector
   - Focus: Installation, indexing, performance

4. **FastAPI**
   - https://fastapi.tiangolo.com/
   - Focus: Request/response models, streaming

### **Additional Reading**

1. **Vector Embeddings**
   - https://www.pinecone.io/learn/vector-embeddings/

2. **RAG Deep Dive**
   - https://blog.langchain.dev/retrieval-augmented-generation-rag-deep-dive/

3. **LLM Evaluation**
   - https://www.anthropic.com/index/evaluating-ai-systems

---

## ✅ FINAL CHECKLIST

### **By End of Week 2:**
- [ ] Project 1 production-ready
- [ ] Docker deployed
- [ ] Professional README
- [ ] Can explain hybrid routing

### **By End of Week 5:**
- [ ] Project 2 MVP working
- [ ] Understands LangChain agents
- [ ] Can demonstrate tool use
- [ ] Basic documentation

### **By End of Week 8:**
- [ ] Project 3 production complete
- [ ] RAG system optimized
- [ ] Comprehensive documentation
- [ ] Performance benchmarked

### **By End of Week 10:**
- [ ] All 3 projects on GitHub
- [ ] Portfolio website/page
- [ ] Interview talking points ready
- [ ] Can explain all projects clearly
- [ ] Resume updated
- [ ] LinkedIn updated
- [ ] Ready to apply for AI/LLM roles

---

## 🎯 SUCCESS METRICS

You'll know you're successful when:

1. **Technical:**
   - Can build LLM-powered systems from scratch
   - Understand when to use AI vs classical approaches
   - Can optimize for cost and performance
   - Comfortable with vector databases

2. **Interview:**
   - Can explain projects clearly in 30 seconds or 30 minutes
   - Answer "why" questions about design decisions
   - Discuss trade-offs confidently
   - Show code and architecture fluently

3. **Portfolio:**
   - 3 working projects, well-documented
   - GitHub profile looks professional
   - Can deploy any project in < 5 minutes
   - Projects demonstrate progression (learning)

4. **Positioning:**
   - "Senior Backend Engineer adding AI skills"
   - Clear value proposition
   - Unique perspective (hybrid systems, cost optimization)
   - Production mindset applied to AI

---

## 📞 GUIDANCE PHILOSOPHY FOR CLAUDE CODE

When guiding Jigar:

1. **Adaptive Complexity:**
   - Week 1-2: Deep, complete, polished
   - Week 3-5: MVP, learn concepts, move on
   - Week 6-8: Full production, flagship project

2. **Learning Style:**
   - Explain WHY, not just WHAT
   - Show trade-offs
   - Encourage questions
   - No buzzwords

3. **Practical Focus:**
   - Always test incrementally
   - Production patterns from start
   - Real metrics (p95, cost, throughput)
   - Portfolio-first thinking

4. **Time Management:**
   - Respect hour estimates
   - Stop projects when time is up
   - MVP is okay for Project 2
   - Focus on completion over perfection

---

**This master plan is COMPLETE. Claude Code has everything needed to guide Jigar through all 10 weeks without external references.**

**Current Status:** Week 1 COMPLETE, Week 2 IN PROGRESS  
**Next Milestone:** Complete Week 2 Phase 1 (Logging)  
**End Goal:** 3 portfolio projects + AI/LLM job-ready

---

*Last Updated: March 21, 2026*  
*Document Version: 1.0 - Complete*
