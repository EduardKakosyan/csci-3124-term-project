from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from typing import Optional
import logging

# Configure root logger to WARNING to reduce noise
logging.basicConfig(level=logging.WARNING)

# Create a custom logger for our app
logger = logging.getLogger("course_app")
logger.setLevel(logging.INFO)

from .models.course import Course
from .db.dynamodb import (
    create_courses_table,
    save_course,
    get_all_courses,
    search_courses,
)

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
async def startup_event():
    """Create DynamoDB table on startup if it doesn't exist."""
    create_courses_table()


@app.get("/")
async def home(request: Request):
    courses = await get_all_courses()
    return templates.TemplateResponse(
        "index.html", {"request": request, "courses": courses}
    )


@app.post("/add_course")
async def add_course(
    request: Request,
    course_code: str = Form(...),
    course_number: str = Form(...),
    description: str = Form(...),
    professor: str = Form(...),
    credit_hours: str = Form(...),  # Changed to str to handle parsing ourselves
):
    try:
        # Log received data
        logger.debug(
            f"Received form data: code={course_code}, number={course_number}, prof={professor}, hours={credit_hours}"
        )

        # Convert credit_hours to int with proper error handling
        try:
            credit_hours_int = int(credit_hours)
        except ValueError:
            return JSONResponse(
                status_code=422,
                content={"detail": "Credit hours must be a valid number"},
            )

        # Create course object
        course = Course(
            course_code=course_code.strip(),
            course_number=course_number.strip(),
            description=description.strip(),
            professor=professor.strip(),
            credit_hours=credit_hours_int,
        )

        # Save to DynamoDB
        success = await save_course(course)
        if not success:
            return JSONResponse(
                status_code=500, content={"detail": "Failed to save course to database"}
            )

        return JSONResponse(content={"success": True})

    except Exception as e:
        logger.exception("Error in add_course")
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.get("/search")
async def search_courses_endpoint(q: Optional[str] = None):
    return await search_courses(q)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
