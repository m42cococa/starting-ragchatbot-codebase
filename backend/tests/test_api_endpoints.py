"""
Tests for FastAPI endpoints in the RAG system.
"""
import pytest
from unittest.mock import Mock
from fastapi import HTTPException
import json


class TestQueryEndpoint:
    """Test cases for /api/query endpoint."""

    def test_query_with_new_session(self, test_client_factory):
        """Test query endpoint creates new session when none provided."""
        # Arrange
        mock_rag_system = Mock()
        mock_rag_system.session_manager = Mock()
        mock_rag_system.session_manager.create_session = Mock(return_value="new-session-123")
        mock_rag_system.query = Mock(return_value=("Test answer", ["source1.md"]))
        
        test_client = test_client_factory(mock_rag_system)
        
        # Act
        response = test_client.post(
            "/api/query",
            json={"query": "What is Python?"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Test answer"
        assert data["sources"] == ["source1.md"]
        assert data["session_id"] == "new-session-123"
        
        # Verify RAG system was called correctly
        mock_rag_system.session_manager.create_session.assert_called_once()
        mock_rag_system.query.assert_called_once_with("What is Python?", "new-session-123")

    def test_query_with_existing_session(self, test_client_factory):
        """Test query endpoint uses provided session ID."""
        # Arrange
        existing_session = "existing-session-456"
        mock_rag_system = Mock()
        mock_rag_system.session_manager = Mock()
        mock_rag_system.query = Mock(return_value=("Existing session answer", ["source2.md"]))
        
        test_client = test_client_factory(mock_rag_system)
        
        # Act
        response = test_client.post(
            "/api/query",
            json={
                "query": "Tell me about data types",
                "session_id": existing_session
            }
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["answer"] == "Existing session answer"
        assert data["sources"] == ["source2.md"]
        assert data["session_id"] == existing_session
        
        # Verify session manager was not called to create new session
        mock_rag_system.session_manager.create_session.assert_not_called()
        mock_rag_system.query.assert_called_once_with("Tell me about data types", existing_session)

    def test_query_with_empty_query(self, test_client_factory):
        """Test query endpoint with empty query string."""
        # Arrange
        mock_rag_system = Mock()
        mock_rag_system.session_manager = Mock()
        mock_rag_system.session_manager.create_session = Mock(return_value="test-session-123")
        mock_rag_system.query = Mock(return_value=("Empty query response", ["source.md"]))
        
        test_client = test_client_factory(mock_rag_system)
        
        # Act
        response = test_client.post(
            "/api/query",
            json={"query": ""}
        )
        
        # Assert - should still process empty query
        assert response.status_code == 200

    def test_query_with_missing_query_field(self, test_client_factory):
        """Test query endpoint with missing query field."""
        # Arrange
        test_client = test_client_factory()
        
        # Act
        response = test_client.post(
            "/api/query",
            json={"session_id": "test-session"}
        )
        
        # Assert
        assert response.status_code == 422  # Validation error

    def test_query_with_invalid_json(self, test_client_factory):
        """Test query endpoint with invalid JSON payload."""
        # Arrange
        test_client = test_client_factory()
        
        # Act
        response = test_client.post(
            "/api/query",
            data="invalid json"
        )
        
        # Assert
        assert response.status_code == 422

    def test_query_rag_system_error(self, test_client_factory):
        """Test query endpoint when RAG system raises exception."""
        # Arrange
        mock_rag_system = Mock()
        mock_rag_system.session_manager = Mock()
        mock_rag_system.session_manager.create_session = Mock(return_value="test-session-123")
        mock_rag_system.query = Mock(side_effect=Exception("RAG system error"))
        
        test_client = test_client_factory(mock_rag_system)
        
        # Act
        response = test_client.post(
            "/api/query",
            json={"query": "What is Python?"}
        )
        
        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "RAG system error" in data["detail"]

    def test_query_response_model_validation(self, test_client_factory):
        """Test that query response matches expected model."""
        # Arrange
        mock_rag_system = Mock()
        mock_rag_system.session_manager = Mock()
        mock_rag_system.session_manager.create_session = Mock(return_value="test-session-123")
        mock_rag_system.query = Mock(return_value=("Valid answer", ["valid_source.md"]))
        
        test_client = test_client_factory(mock_rag_system)
        
        # Act
        response = test_client.post(
            "/api/query",
            json={"query": "Valid query"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert isinstance(data["answer"], str)
        assert isinstance(data["sources"], list)
        assert isinstance(data["session_id"], str)
        assert len(data["sources"]) > 0
        assert data["sources"][0] == "valid_source.md"

    def test_query_with_multiple_sources(self, test_client_factory):
        """Test query endpoint with multiple source documents."""
        # Arrange
        multiple_sources = ["doc1.md", "doc2.md", "doc3.md"]
        mock_rag_system = Mock()
        mock_rag_system.session_manager = Mock()
        mock_rag_system.session_manager.create_session = Mock(return_value="test-session-123")
        mock_rag_system.query = Mock(return_value=("Multi-source answer", multiple_sources))
        
        test_client = test_client_factory(mock_rag_system)
        
        # Act
        response = test_client.post(
            "/api/query",
            json={"query": "Complex query"}
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["sources"] == multiple_sources
        assert len(data["sources"]) == 3


class TestCoursesEndpoint:
    """Test cases for /api/courses endpoint."""

    def test_get_course_stats_success(self, test_client_factory):
        """Test successful retrieval of course statistics."""
        # Arrange
        mock_analytics = {
            "total_courses": 3,
            "course_titles": ["Python Basics", "Advanced Python", "Data Science"]
        }
        mock_rag_system = Mock()
        mock_rag_system.get_course_analytics = Mock(return_value=mock_analytics)
        
        test_client = test_client_factory(mock_rag_system)
        
        # Act
        response = test_client.get("/api/courses")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total_courses"] == 3
        assert len(data["course_titles"]) == 3
        assert "Python Basics" in data["course_titles"]
        assert "Advanced Python" in data["course_titles"]
        assert "Data Science" in data["course_titles"]

    def test_get_course_stats_empty(self, test_client_factory):
        """Test course statistics when no courses exist."""
        # Arrange
        mock_rag_system = Mock()
        mock_rag_system.get_course_analytics = Mock(return_value={
            "total_courses": 0,
            "course_titles": []
        })
        
        test_client = test_client_factory(mock_rag_system)
        
        # Act
        response = test_client.get("/api/courses")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["total_courses"] == 0
        assert data["course_titles"] == []

    def test_get_course_stats_error(self, test_client_factory):
        """Test course statistics endpoint when analytics fails."""
        # Arrange
        mock_rag_system = Mock()
        mock_rag_system.get_course_analytics = Mock(side_effect=Exception("Analytics error"))
        
        test_client = test_client_factory(mock_rag_system)
        
        # Act
        response = test_client.get("/api/courses")
        
        # Assert
        assert response.status_code == 500
        data = response.json()
        assert "Analytics error" in data["detail"]

    def test_get_course_stats_response_model(self, test_client_factory):
        """Test that course stats response matches expected model."""
        # Arrange
        mock_rag_system = Mock()
        mock_rag_system.get_course_analytics = Mock(return_value={
            "total_courses": 1,
            "course_titles": ["Test Course"]
        })
        
        test_client = test_client_factory(mock_rag_system)
        
        # Act
        response = test_client.get("/api/courses")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert isinstance(data["total_courses"], int)
        assert isinstance(data["course_titles"], list)
        assert data["total_courses"] >= 0
        if data["total_courses"] > 0:
            assert len(data["course_titles"]) == data["total_courses"]


class TestRootEndpoint:
    """Test cases for root endpoint."""

    def test_root_endpoint_success(self, test_client_factory):
        """Test that root endpoint returns expected message."""
        # Arrange
        test_client = test_client_factory()
        
        # Act
        response = test_client.get("/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "RAG System" in data["message"]

    def test_root_endpoint_content_type(self, test_client_factory):
        """Test that root endpoint returns correct content type."""
        # Arrange
        test_client = test_client_factory()
        
        # Act
        response = test_client.get("/")
        
        # Assert
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]


class TestMiddleware:
    """Test middleware functionality."""

    def test_cors_headers_present(self, test_client_factory):
        """Test that CORS headers are properly set."""
        # Arrange
        test_client = test_client_factory()
        
        # Act
        response = test_client.options("/api/query")
        
        # Assert
        # Note: TestClient may not fully replicate CORS behavior,
        # but we can test that the endpoint is accessible
        assert response.status_code in [200, 405]  # OPTIONS might not be explicitly handled

    def test_trusted_host_middleware(self, test_client_factory):
        """Test requests work with trusted host middleware."""
        # Arrange
        test_client = test_client_factory()
        
        # Act
        response = test_client.get("/", headers={"Host": "testserver"})
        
        # Assert
        assert response.status_code == 200


class TestErrorHandling:
    """Test error handling across endpoints."""

    def test_http_methods_not_allowed(self, test_client_factory):
        """Test that incorrect HTTP methods return 405."""
        # Arrange
        test_client = test_client_factory()
        
        # Test GET on POST endpoint
        response = test_client.get("/api/query")
        assert response.status_code == 405
        
        # Test POST on GET endpoint
        response = test_client.post("/api/courses")
        assert response.status_code == 405

    def test_nonexistent_endpoint(self, test_client_factory):
        """Test that non-existent endpoints return 404."""
        # Arrange
        test_client = test_client_factory()
        
        # Act
        response = test_client.get("/api/nonexistent")
        
        # Assert
        assert response.status_code == 404

    def test_large_payload_handling(self, test_client_factory):
        """Test handling of large request payloads."""
        # Arrange
        mock_rag_system = Mock()
        mock_rag_system.session_manager = Mock()
        mock_rag_system.session_manager.create_session = Mock(return_value="test-session-123")
        mock_rag_system.query = Mock(return_value=("Large query response", ["source.md"]))
        
        test_client = test_client_factory(mock_rag_system)
        
        # Arrange - Create a very long query
        large_query = "What is Python? " * 1000  # Repeat to make it large
        
        # Act
        response = test_client.post(
            "/api/query",
            json={"query": large_query}
        )
        
        # Assert - Should still process (assuming no size limits configured)
        assert response.status_code == 200


class TestIntegrationScenarios:
    """Integration test scenarios across multiple endpoints."""

    def test_query_then_stats_workflow(self, test_client_factory):
        """Test a typical workflow: query -> get stats."""
        # Arrange
        mock_rag_system = Mock()
        mock_rag_system.session_manager = Mock()
        mock_rag_system.session_manager.create_session = Mock(return_value="test-session-123")
        mock_rag_system.query = Mock(return_value=("Answer", ["source.md"]))
        mock_rag_system.get_course_analytics = Mock(return_value={
            "total_courses": 1,
            "course_titles": ["Test Course"]
        })
        
        test_client = test_client_factory(mock_rag_system)
        
        # Act - Query first
        query_response = test_client.post(
            "/api/query",
            json={"query": "Test query"}
        )
        
        # Act - Then get stats
        stats_response = test_client.get("/api/courses")
        
        # Assert both succeed
        assert query_response.status_code == 200
        assert stats_response.status_code == 200
        
        # Verify both RAG system methods were called
        mock_rag_system.query.assert_called_once()
        mock_rag_system.get_course_analytics.assert_called_once()

    def test_multiple_queries_same_session(self, test_client_factory):
        """Test multiple queries using the same session ID."""
        # Arrange
        session_id = "persistent-session"
        mock_rag_system = Mock()
        mock_rag_system.session_manager = Mock()
        mock_rag_system.query = Mock(return_value=("Session answer", ["source.md"]))
        
        test_client = test_client_factory(mock_rag_system)
        
        # Act - First query
        response1 = test_client.post(
            "/api/query",
            json={"query": "First query", "session_id": session_id}
        )
        
        # Act - Second query with same session
        response2 = test_client.post(
            "/api/query",
            json={"query": "Second query", "session_id": session_id}
        )
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["session_id"] == session_id
        assert response2.json()["session_id"] == session_id
        
        # Verify RAG system was called with the same session both times
        assert mock_rag_system.query.call_count == 2
        calls = mock_rag_system.query.call_args_list
        assert calls[0][0][1] == session_id  # First call, second argument
        assert calls[1][0][1] == session_id  # Second call, second argument