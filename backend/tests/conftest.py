"""
Shared fixtures and configuration for RAG system tests.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from typing import List, Dict, Any
import tempfile
import os

# Import models and config
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config import Config
from models import Course, Lesson, CourseChunk


@pytest.fixture
def test_config():
    """Create test configuration with safe defaults."""
    return Config(
        ANTHROPIC_API_KEY="test-api-key",
        ANTHROPIC_MODEL="claude-sonnet-4-20250514",
        EMBEDDING_MODEL="all-MiniLM-L6-v2",
        CHUNK_SIZE=800,
        CHUNK_OVERLAP=100,
        MAX_RESULTS=5,
        MAX_HISTORY=2,
        CHROMA_PATH="./test_chroma_db"
    )


@pytest.fixture
def sample_course():
    """Sample course data for testing."""
    return Course(
        title="Introduction to Python",
        lessons=[
            Lesson(number=1, title="Python Basics", link="http://example.com/lesson1"),
            Lesson(number=2, title="Data Types", link="http://example.com/lesson2"),
            Lesson(number=3, title="Control Flow")
        ]
    )


@pytest.fixture
def sample_course_chunks(sample_course):
    """Sample course chunks for testing."""
    return [
        CourseChunk(
            course_title=sample_course.title,
            lesson_number=1,
            lesson_title="Python Basics",
            chunk_index=0,
            content="Python is a programming language that lets you work quickly and integrate systems more effectively.",
            metadata={"source": "lesson1.md", "lesson_link": "http://example.com/lesson1"}
        ),
        CourseChunk(
            course_title=sample_course.title,
            lesson_number=1,
            lesson_title="Python Basics", 
            chunk_index=1,
            content="Python supports multiple programming paradigms including structured, object-oriented and functional programming.",
            metadata={"source": "lesson1.md", "lesson_link": "http://example.com/lesson1"}
        ),
        CourseChunk(
            course_title=sample_course.title,
            lesson_number=2,
            lesson_title="Data Types",
            chunk_index=0,
            content="Python has several built-in data types: int, float, str, bool, list, dict, tuple, and set.",
            metadata={"source": "lesson2.md", "lesson_link": "http://example.com/lesson2"}
        )
    ]


@pytest.fixture
def mock_document_processor():
    """Mock DocumentProcessor for testing."""
    mock = Mock()
    mock.process_course_document = Mock()
    mock.process_course_folder = Mock()
    return mock


@pytest.fixture
def mock_vector_store():
    """Mock VectorStore for testing."""
    mock = Mock()
    mock.add_course_metadata = Mock()
    mock.add_course_content = Mock()
    mock.search_similar_content = Mock()
    mock.get_course_analytics = Mock()
    mock.collection = Mock()
    return mock


@pytest.fixture
def mock_ai_generator():
    """Mock AIGenerator for testing."""
    mock = Mock()
    mock.generate_response = AsyncMock()
    mock.generate_sequential_response = AsyncMock()
    return mock


@pytest.fixture
def mock_session_manager():
    """Mock SessionManager for testing."""
    mock = Mock()
    mock.create_session = Mock(return_value="test-session-123")
    mock.add_message = Mock()
    mock.get_history = Mock(return_value=[])
    mock.clear_session = Mock()
    return mock


@pytest.fixture
def mock_search_tool():
    """Mock CourseSearchTool for testing."""
    mock = Mock()
    mock.execute = AsyncMock()
    mock.get_tool_definition = Mock()
    return mock


@pytest.fixture
def mock_tool_manager():
    """Mock ToolManager for testing."""
    mock = Mock()
    mock.register_tool = Mock()
    mock.get_tool_definitions = Mock(return_value=[])
    mock.execute_tool = AsyncMock()
    return mock


@pytest.fixture
def mock_rag_system(test_config, mock_document_processor, mock_vector_store, 
                   mock_ai_generator, mock_session_manager, mock_search_tool, mock_tool_manager):
    """Mock RAGSystem with all dependencies mocked."""
    with patch('rag_system.DocumentProcessor', return_value=mock_document_processor), \
         patch('rag_system.VectorStore', return_value=mock_vector_store), \
         patch('rag_system.AIGenerator', return_value=mock_ai_generator), \
         patch('rag_system.SessionManager', return_value=mock_session_manager), \
         patch('rag_system.ToolManager', return_value=mock_tool_manager), \
         patch('rag_system.CourseSearchTool', return_value=mock_search_tool):
        
        from rag_system import RAGSystem
        rag_system = RAGSystem(test_config)
        
        # Set up default mock behaviors
        mock_vector_store.search_similar_content.return_value = []
        mock_vector_store.get_course_analytics.return_value = {
            "total_courses": 1,
            "course_titles": ["Introduction to Python"]
        }
        mock_ai_generator.generate_sequential_response.return_value = (
            "This is a test response about Python programming.",
            ["lesson1.md", "lesson2.md"]
        )
        
        return rag_system


@pytest.fixture
def test_client_factory():
    """Factory function to create test clients with different configurations."""
    def _create_test_client(mock_rag_system=None):
        """Create a FastAPI test client avoiding static file mount issues."""
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.middleware.trustedhost import TrustedHostMiddleware
        from pydantic import BaseModel
        from typing import List, Optional
        import warnings
        warnings.filterwarnings("ignore")
        
        # Create a test-specific FastAPI app
        test_app = FastAPI(title="Course Materials RAG System - Test", root_path="")
        
        # Add middleware
        test_app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"]
        )
        test_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"],
        )
        
        # Request/Response models
        class QueryRequest(BaseModel):
            query: str
            session_id: Optional[str] = None

        class QueryResponse(BaseModel):
            answer: str
            sources: List[str]
            session_id: str

        class CourseStats(BaseModel):
            total_courses: int
            course_titles: List[str]
        
        # Use provided mock or create a default one
        if mock_rag_system is None:
            mock_rag_system = Mock()
            mock_rag_system.session_manager = Mock()
            mock_rag_system.session_manager.create_session = Mock(return_value="test-session-123")
            mock_rag_system.query = Mock(return_value=("Test response", ["test_source.md"]))
            mock_rag_system.get_course_analytics = Mock(return_value={
                "total_courses": 1,
                "course_titles": ["Test Course"]
            })
        
        # API Endpoints
        @test_app.post("/api/query", response_model=QueryResponse)
        async def query_documents(request: QueryRequest):
            try:
                session_id = request.session_id
                if not session_id:
                    session_id = mock_rag_system.session_manager.create_session()
                
                answer, sources = mock_rag_system.query(request.query, session_id)
                
                return QueryResponse(
                    answer=answer,
                    sources=sources,
                    session_id=session_id
                )
            except Exception as e:
                from fastapi import HTTPException
                raise HTTPException(status_code=500, detail=str(e))

        @test_app.get("/api/courses", response_model=CourseStats)
        async def get_course_stats():
            try:
                analytics = mock_rag_system.get_course_analytics()
                return CourseStats(
                    total_courses=analytics["total_courses"],
                    course_titles=analytics["course_titles"]
                )
            except Exception as e:
                from fastapi import HTTPException
                raise HTTPException(status_code=500, detail=str(e))

        @test_app.get("/")
        async def root():
            return {"message": "Course Materials RAG System - Test Mode"}
        
        return TestClient(test_app)
    
    return _create_test_client


@pytest.fixture
def test_client(test_client_factory, mock_rag_system):
    """Default test client with mocked RAG system."""
    return test_client_factory(mock_rag_system)


@pytest.fixture
def sample_query_request():
    """Sample API request data for testing."""
    return {
        "query": "What are Python data types?",
        "session_id": None
    }


@pytest.fixture
def expected_query_response():
    """Expected API response data for testing."""
    return {
        "answer": "This is a test response about Python programming.",
        "sources": ["lesson1.md", "lesson2.md"],
        "session_id": "test-session-123"
    }


@pytest.fixture
def expected_course_stats():
    """Expected course statistics response."""
    return {
        "total_courses": 1,
        "course_titles": ["Introduction to Python"]
    }


@pytest.fixture
def temp_docs_directory():
    """Create a temporary directory with test documents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create sample course files
        lesson1_path = os.path.join(temp_dir, "lesson1.md")
        lesson2_path = os.path.join(temp_dir, "lesson2.md")
        
        with open(lesson1_path, "w") as f:
            f.write("""# Lesson 1: Python Basics
            
Python is a programming language that lets you work quickly and integrate systems more effectively.
Python supports multiple programming paradigms including structured, object-oriented and functional programming.
""")
        
        with open(lesson2_path, "w") as f:
            f.write("""# Lesson 2: Data Types

Python has several built-in data types: int, float, str, bool, list, dict, tuple, and set.
These data types are fundamental to Python programming.
""")
        
        yield temp_dir


# Test data constants
SAMPLE_ANTHROPIC_RESPONSE = {
    "content": [
        {
            "type": "text", 
            "text": "This is a test response about Python programming."
        }
    ],
    "usage": {"input_tokens": 100, "output_tokens": 20}
}

SAMPLE_SEARCH_RESULTS = [
    {
        "content": "Python is a programming language that lets you work quickly",
        "metadata": {"source": "lesson1.md", "lesson_number": 1}
    },
    {
        "content": "Python has several built-in data types: int, float, str, bool",
        "metadata": {"source": "lesson2.md", "lesson_number": 2}
    }
]


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Cleanup any test database files after each test."""
    yield
    # Clean up any test ChromaDB files
    import shutil
    test_db_path = "./test_chroma_db"
    if os.path.exists(test_db_path):
        shutil.rmtree(test_db_path)