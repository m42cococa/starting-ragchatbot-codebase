# RAG System Question-to-Response Flow

```mermaid
flowchart TD
    Start([User asks question]) --> WebUI[Web Interface<br/>frontend/]
    WebUI --> API[FastAPI Endpoint<br/>backend/app.py]
    
    API --> Session[Session Manager<br/>backend/session_manager.py]
    Session --> |Store query| SessionDB[(Session History)]
    
    API --> RAG[RAG System<br/>backend/rag_system.py]
    
    RAG --> Search[Search Tools<br/>backend/search_tools.py]
    Search --> Vector[Vector Store<br/>backend/vector_store.py]
    Vector --> ChromaDB[(ChromaDB<br/>Vector Database)]
    
    ChromaDB --> |Semantic search| Embeddings[Sentence Transformers<br/>Generate embeddings]
    Embeddings --> |Find similar docs| ChromaDB
    ChromaDB --> |Return relevant chunks| Vector
    
    Vector --> |Relevant documents| RAG
    
    RAG --> AI[AI Generator<br/>backend/ai_generator.py]
    AI --> Claude[Anthropic Claude API]
    
    Claude --> |Generate response| AI
    AI --> |Formatted answer| RAG
    
    RAG --> |Answer + Sources| API
    API --> |Update session| Session
    Session --> SessionDB
    
    API --> Response[QueryResponse<br/>backend/models.py]
    Response --> WebUI
    WebUI --> End([User receives answer<br/>with source citations])
    
    style Start fill:#e1f5fe
    style End fill:#c8e6c9
    style Claude fill:#fff3e0
    style ChromaDB fill:#f3e5f5
    style SessionDB fill:#f3e5f5
```

## Process Flow Description

1. **User Input**: User submits a question through the web interface
2. **API Request**: Frontend sends POST request to `/query` endpoint
3. **Session Management**: System creates/retrieves session for conversation tracking
4. **RAG Processing**: Core RAG system orchestrates the retrieval and generation
5. **Document Retrieval**: 
   - Search tools create embeddings of the query
   - Vector store performs semantic search in ChromaDB
   - Returns most relevant document chunks
6. **AI Generation**:
   - AI Generator formats context with retrieved documents
   - Sends to Claude API with system prompt and context
   - Receives intelligent, context-aware response
7. **Response Delivery**: Answer with source citations returned to user
8. **Session Update**: Conversation history updated for continuity