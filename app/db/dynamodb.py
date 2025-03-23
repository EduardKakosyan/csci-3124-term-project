import boto3
import os
import logging
from dotenv import load_dotenv
from typing import List, Optional
from ..models.course import Course
from .s3 import refresh_presigned_url

# Configure logging levels for boto3 and related libraries
logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Load environment variables
load_dotenv()

# Initialize DynamoDB client
dynamodb = boto3.resource(
    "dynamodb",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
    region_name=os.getenv("AWS_REGION"),
)

# Table name
COURSES_TABLE = os.getenv("DYNAMODB_TABLE", "dalhousie-courses")


def create_courses_table():
    """Create the Courses table if it doesn't exist."""
    try:
        table = dynamodb.create_table(
            TableName=COURSES_TABLE,
            KeySchema=[{"AttributeName": "course_code", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "course_code", "AttributeType": "S"}
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )
        table.wait_until_exists()
        print(f"Table {COURSES_TABLE} created successfully")
    except dynamodb.meta.client.exceptions.ResourceInUseException:
        print(f"Table {COURSES_TABLE} already exists")
    except Exception as e:
        print(f"Error creating table: {str(e)}")


def get_table():
    """Get the Courses table."""
    return dynamodb.Table(COURSES_TABLE)


async def save_course(course: Course) -> bool:
    """Save a course to DynamoDB."""
    try:
        table = get_table()
        item = {
            "course_code": course.course_code,
            "course_number": course.course_number,
            "description": course.description,
            "professor": course.professor,
            "credit_hours": course.credit_hours,
            "course_code_lower": course.course_code.lower(),
        }

        # Add file information if present
        if course.syllabus_key:
            item["syllabus_key"] = course.syllabus_key
            item["syllabus_filename"] = course.syllabus_filename

        table.put_item(Item=item)
        return True
    except Exception as e:
        print(f"Error saving course: {str(e)}")
        return False


async def get_all_courses() -> List[Course]:
    """Get all courses from DynamoDB."""
    try:
        table = get_table()
        response = table.scan()
        courses = []
        for item in response.get("Items", []):
            course_data = {
                "course_code": item["course_code"],
                "course_number": item["course_number"],
                "description": item["description"],
                "professor": item["professor"],
                "credit_hours": item["credit_hours"],
            }

            # Add file information and generate fresh presigned URL if needed
            if "syllabus_key" in item:
                course_data["syllabus_key"] = item["syllabus_key"]
                course_data["syllabus_filename"] = item["syllabus_filename"]
                course_data["syllabus_url"] = refresh_presigned_url(
                    item["syllabus_key"]
                )

            courses.append(Course(**course_data))
        return courses
    except Exception as e:
        print(f"Error getting courses: {str(e)}")
        return []


async def search_courses(query: str) -> List[Course]:
    """Search courses by course code in DynamoDB."""
    try:
        if not query:
            return await get_all_courses()

        query = query.lower()
        table = get_table()

        # Only search by course code
        response = table.scan(
            FilterExpression="contains(course_code_lower, :q)",
            ExpressionAttributeValues={":q": query},
        )

        courses = []
        for item in response.get("Items", []):
            course_data = {
                "course_code": item["course_code"],
                "course_number": item["course_number"],
                "description": item["description"],
                "professor": item["professor"],
                "credit_hours": item["credit_hours"],
            }

            # Add file information and generate fresh presigned URL if needed
            if "syllabus_key" in item:
                course_data["syllabus_key"] = item["syllabus_key"]
                course_data["syllabus_filename"] = item["syllabus_filename"]
                course_data["syllabus_url"] = refresh_presigned_url(
                    item["syllabus_key"]
                )

            courses.append(Course(**course_data))
        return courses

    except Exception as e:
        print(f"Error searching courses: {str(e)}")
        return []
