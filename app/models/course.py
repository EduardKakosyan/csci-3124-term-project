from pydantic import BaseModel, Field, constr


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
