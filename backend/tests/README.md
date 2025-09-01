# RAG System Testing Framework

This directory contains comprehensive tests for the RAG (Retrieval-Augmented Generation) system, providing both API endpoint testing and unit component testing.

## Test Structure

```
backend/tests/
├── README.md                 # This file - testing documentation
├── __init__.py              # Makes tests a Python package
├── conftest.py              # Shared fixtures and test configuration
├── test_api_endpoints.py    # FastAPI endpoint tests
└── test_models.py           # Pydantic model validation tests
```

## Test Coverage

### API Endpoint Tests (`test_api_endpoints.py`)
- **Query Endpoint (`/api/query`)**: Tests for session management, request/response validation, error handling
- **Courses Endpoint (`/api/courses`)**: Tests for course analytics and statistics
- **Root Endpoint (`/`)**: Basic connectivity and response format tests
- **Middleware**: CORS and trusted host middleware functionality
- **Error Handling**: HTTP method validation, 404/500 error scenarios
- **Integration Scenarios**: Multi-endpoint workflows and session persistence

### Model Tests (`test_models.py`)
- **Lesson Model**: Creation, validation, and serialization tests
- **Course Model**: Course-lesson relationships and data integrity
- **CourseChunk Model**: Vector storage chunk validation and structure
- **Integration Tests**: Cross-model relationships and data flow

## Key Features

### Test Fixtures (`conftest.py`)
- **Mock RAG System**: Complete mock implementation avoiding external dependencies
- **Test Client Factory**: Flexible FastAPI test client creation avoiding static file mount issues
- **Sample Data**: Pre-configured course, lesson, and chunk data for consistent testing
- **Cleanup**: Automatic cleanup of temporary test databases and files

### Pytest Configuration (`pyproject.toml`)
- **Test Discovery**: Automatic discovery of test files and functions
- **Async Support**: Full async/await support for FastAPI testing
- **Warning Management**: Filtered warnings for clean test output
- **Verbose Output**: Detailed test execution reporting

## Running Tests

### All Tests
```bash
# From backend directory
uv run pytest tests/ -v
```

### Specific Test Files
```bash
# API endpoint tests only
uv run pytest tests/test_api_endpoints.py -v

# Model tests only
uv run pytest tests/test_models.py -v
```

### Specific Test Classes
```bash
# Test only query endpoint functionality
uv run pytest tests/test_api_endpoints.py::TestQueryEndpoint -v

# Test only course model validation
uv run pytest tests/test_models.py::TestCourse -v
```

### Individual Tests
```bash
# Test specific functionality
uv run pytest tests/test_api_endpoints.py::TestQueryEndpoint::test_query_with_new_session -v
```

## Test Design Principles

### Mock-First Approach
- All external dependencies (ChromaDB, Anthropic API, file system) are mocked
- Tests focus on business logic rather than integration complexity
- Fast execution with predictable, repeatable results

### Isolated Test Environment
- Each test uses fresh mock objects to avoid state contamination
- Test client factory pattern allows customizable test scenarios
- Automatic cleanup prevents test artifacts from affecting subsequent runs

### Comprehensive Coverage
- **Happy Path**: Normal operation scenarios with valid inputs
- **Edge Cases**: Empty inputs, boundary conditions, unusual but valid scenarios
- **Error Conditions**: Invalid inputs, system failures, network issues
- **Integration**: Multi-component workflows and data flow validation

### FastAPI Test Strategy
- **Separate Test App**: Avoids static file mounting issues by creating test-specific FastAPI app
- **Request/Response Testing**: Validates HTTP status codes, JSON structure, and data integrity
- **Middleware Testing**: Ensures CORS, security, and routing middleware function correctly

## Adding New Tests

### For New API Endpoints
1. Add endpoint definition to test client factory in `conftest.py`
2. Create new test class in `test_api_endpoints.py`
3. Include tests for success cases, validation errors, and system failures

### For New Models
1. Add model import to `test_models.py`
2. Create test class with creation, validation, and serialization tests
3. Add integration tests if the model interacts with existing models

### For New Components
1. Create new test file following naming convention `test_component.py`
2. Add necessary fixtures to `conftest.py`
3. Follow existing patterns for mock usage and test structure

## Dependencies

The testing framework requires these packages (automatically installed with `uv sync`):
- **pytest**: Core testing framework
- **pytest-asyncio**: Async test support for FastAPI
- **httpx**: HTTP client for API testing (used by FastAPI TestClient)
- **fastapi[testing]**: FastAPI testing utilities

## Performance Considerations

- **Mock Usage**: Prevents expensive external API calls and database operations
- **Parallel Execution**: Tests can be run in parallel with `pytest -n auto` (requires pytest-xdist)
- **Selective Execution**: Run only relevant test subsets during development

## Troubleshooting

### Common Issues

**Import Errors**: Ensure you're running tests from the `backend` directory and all dependencies are installed
```bash
cd backend && uv sync && uv run pytest
```

**Mock Failures**: Check that mock configurations in test methods match the expected method signatures

**Async Warnings**: Verify `asyncio_mode = "auto"` is set in pytest configuration

**Test Discovery**: Ensure test files follow naming convention (`test_*.py` or `*_test.py`)

### Debug Mode
```bash
# Run with detailed output and no capture for debugging
uv run pytest tests/ -v -s --tb=long
```

### Test Coverage Analysis
```bash
# Run with coverage reporting (requires pytest-cov)
uv run pytest tests/ --cov=backend --cov-report=html
```