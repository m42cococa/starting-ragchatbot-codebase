"""
Tests for Pydantic models and data validation.
"""
import pytest
from pydantic import ValidationError
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import Course, Lesson, CourseChunk


class TestLesson:
    """Test cases for Lesson model."""

    def test_lesson_creation_full(self):
        """Test creating a lesson with all fields."""
        lesson = Lesson(
            lesson_number=1,
            title="Introduction to Python",
            lesson_link="https://example.com/lesson1"
        )
        
        assert lesson.lesson_number == 1
        assert lesson.title == "Introduction to Python"
        assert lesson.lesson_link == "https://example.com/lesson1"

    def test_lesson_creation_without_link(self):
        """Test creating a lesson without optional link field."""
        lesson = Lesson(
            lesson_number=2,
            title="Python Basics"
        )
        
        assert lesson.lesson_number == 2
        assert lesson.title == "Python Basics"
        assert lesson.lesson_link is None

    def test_lesson_validation_missing_required_fields(self):
        """Test lesson validation fails with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            Lesson(title="Missing Number")
        
        assert "lesson_number" in str(exc_info.value)

    def test_lesson_validation_invalid_types(self):
        """Test lesson validation fails with invalid field types."""
        with pytest.raises(ValidationError):
            Lesson(lesson_number="not_an_int", title="Valid Title")


class TestCourse:
    """Test cases for Course model."""

    def test_course_creation_with_lessons(self):
        """Test creating a course with lessons."""
        lessons = [
            Lesson(lesson_number=1, title="Lesson 1", lesson_link="http://example.com/1"),
            Lesson(lesson_number=2, title="Lesson 2")
        ]
        
        course = Course(
            title="Python Programming",
            lessons=lessons
        )
        
        assert course.title == "Python Programming"
        assert len(course.lessons) == 2
        assert course.lessons[0].lesson_number == 1
        assert course.lessons[1].title == "Lesson 2"

    def test_course_creation_empty_lessons(self):
        """Test creating a course with empty lessons list."""
        course = Course(
            title="Empty Course",
            lessons=[]
        )
        
        assert course.title == "Empty Course"
        assert course.lessons == []

    def test_course_validation_missing_title(self):
        """Test course validation fails without title."""
        with pytest.raises(ValidationError) as exc_info:
            Course(lessons=[])
        
        assert "title" in str(exc_info.value)

    def test_course_validation_invalid_lessons(self):
        """Test course validation fails with invalid lesson data."""
        with pytest.raises(ValidationError):
            Course(
                title="Valid Title",
                lessons=["invalid_lesson_data"]
            )


class TestCourseChunk:
    """Test cases for CourseChunk model."""

    def test_course_chunk_creation_full(self):
        """Test creating a course chunk with all fields."""
        chunk = CourseChunk(
            content="Python is a programming language.",
            course_title="Python Course",
            lesson_number=1,
            chunk_index=0
        )
        
        assert chunk.content == "Python is a programming language."
        assert chunk.course_title == "Python Course"
        assert chunk.lesson_number == 1
        assert chunk.chunk_index == 0

    def test_course_chunk_creation_minimal(self):
        """Test creating a course chunk with minimal required fields."""
        chunk = CourseChunk(
            content="Minimal content",
            course_title="Minimal Course",
            chunk_index=0
        )
        
        assert chunk.content == "Minimal content"
        assert chunk.course_title == "Minimal Course"
        assert chunk.lesson_number is None

    def test_course_chunk_validation_missing_fields(self):
        """Test course chunk validation fails with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            CourseChunk(
                course_title="Valid Course",
                lesson_number=1,
                # Missing content and chunk_index
            )
        
        error_str = str(exc_info.value)
        assert "content" in error_str
        assert "chunk_index" in error_str

    def test_course_chunk_validation_invalid_types(self):
        """Test course chunk validation fails with invalid field types."""
        with pytest.raises(ValidationError):
            CourseChunk(
                content="Valid content",
                course_title="Valid Course",
                lesson_number="not_an_int",  # Should be int
                chunk_index=0
            )

    def test_course_chunk_negative_indices(self):
        """Test course chunk accepts negative indices (no validation constraints)."""
        # The actual model doesn't have constraints on negative values
        chunk = CourseChunk(
            content="Valid content",
            course_title="Valid Course",
            lesson_number=-1,
            chunk_index=-1
        )
        
        assert chunk.lesson_number == -1
        assert chunk.chunk_index == -1


class TestModelIntegration:
    """Integration tests for models working together."""

    def test_course_with_lessons_serialization(self):
        """Test that course with lessons can be serialized and deserialized."""
        original_course = Course(
            title="Complete Python Course",
            lessons=[
                Lesson(lesson_number=1, title="Basics", lesson_link="http://example.com/1"),
                Lesson(lesson_number=2, title="Advanced"),
                Lesson(lesson_number=3, title="Expert", lesson_link="http://example.com/3")
            ]
        )
        
        # Test serialization
        course_dict = original_course.model_dump()
        assert course_dict["title"] == "Complete Python Course"
        assert len(course_dict["lessons"]) == 3
        assert course_dict["lessons"][1]["lesson_link"] is None
        
        # Test deserialization
        reconstructed_course = Course.model_validate(course_dict)
        assert reconstructed_course.title == original_course.title
        assert len(reconstructed_course.lessons) == len(original_course.lessons)
        assert reconstructed_course.lessons[0].lesson_link == original_course.lessons[0].lesson_link

    def test_course_chunk_from_course_lesson(self):
        """Test creating course chunks that reference course and lesson data."""
        course = Course(
            title="Data Science Course",
            lessons=[
                Lesson(lesson_number=1, title="Introduction to Data Science"),
                Lesson(lesson_number=2, title="Data Analysis")
            ]
        )
        
        # Create chunk referencing the course data
        chunk = CourseChunk(
            content="Data science is an interdisciplinary field.",
            course_title=course.title,
            lesson_number=course.lessons[0].lesson_number,
            chunk_index=0
        )
        
        assert chunk.course_title == course.title
        assert chunk.lesson_number == course.lessons[0].lesson_number
        assert chunk.content == "Data science is an interdisciplinary field."

    def test_empty_strings_validation(self):
        """Test that empty strings are handled appropriately."""
        # Empty title should be allowed (Pydantic doesn't prevent empty strings by default)
        course = Course(title="", lessons=[])
        assert course.title == ""
        
        # Empty lesson title should be allowed
        lesson = Lesson(lesson_number=1, title="")
        assert lesson.title == ""
        
        # Empty content in chunk should be valid
        chunk = CourseChunk(
            content="",  # Empty content
            course_title="Valid Course",
            lesson_number=1,
            chunk_index=0
        )
        assert chunk.content == ""