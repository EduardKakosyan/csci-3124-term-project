from pydantic import BaseModel, Field, constr
from typing import Optional


class Course(BaseModel):
    course_code: constr(strip_whitespace=True, min_length=1) = Field(
        ..., description="Course code (e.g., CSCI3130)"
    )
    course_number: constr(strip_whitespace=True, min_length=1) = Field(
        ..., description="Course name/number"
    )
    description: constr(strip_whitespace=True, min_length=1) = Field(
        ..., description="Course description"
    )
    professor: constr(strip_whitespace=True, min_length=1) = Field(
        ..., description="Professor name"
    )
    credit_hours: int = Field(..., ge=1, le=6, description="Number of credit hours")
    syllabus_key: Optional[str] = Field(
        None, description="S3 object key for the syllabus file"
    )
    syllabus_filename: Optional[str] = Field(
        None, description="Original filename of the syllabus"
    )
    syllabus_url: Optional[str] = Field(
        None, description="Presigned URL for the syllabus file"
    )
