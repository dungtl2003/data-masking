import logging
from typing import Any, Dict, List
from fastapi import APIRouter
import bcrypt
from fastapi.responses import JSONResponse
from mysql.connector.types import RowItemType, RowType

from app.api.v1.persons.model import Person
from preload import mydb, settings


api_router = APIRouter(prefix="/persons")


@api_router.post("/", status_code=201)
async def create_user(person: Person):
    logger = logging.getLogger("uvicorn")

    sql = "SELECT id, username, email FROM person WHERE username = %s OR email = %s"
    val = (person.username, person.email)
    mycursor = mydb.cursor()
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    if result:
        if type(result) is not RowType and type(result) is not tuple:
            logger.debug(f"Invalid result type: {type(result)}")
            return JSONResponse(
                status_code=500, content={"message": "Internal server error"}
            )

        username = str(result[1])
        if username == person.username:
            logger.debug("Username already exists")
            return JSONResponse(
                status_code=400,
                content={"message": "Username already exists"},
            )

        logger.debug("Email already exists")
        return JSONResponse(
            status_code=400,
            content={"message": "Email already exists"},
        )

    logger.debug("creating user")

    password_bytes = person.password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=settings.rounds)
    hashed = bcrypt.hashpw(password_bytes, salt)

    mycursor = mydb.cursor()
    sql = "INSERT INTO person (email, username, password, gender, city, phone_number) VALUES (%s, %s, %s, %s, %s, %s)"
    val = (
        person.email,
        person.username,
        hashed,
        person.gender,
        person.city,
        person.phone_number,
    )
    mycursor.execute(sql, val)
    mydb.commit()

    return {"message": "User created"}


@api_router.get("/")
async def get_users() -> List[RowType | Dict[str, RowItemType]] | Any:
    logger = logging.getLogger("uvicorn")
    logger.debug("getting users")
    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute(
        "SELECT id, email, username, gender, city, phone_number FROM person"
    )
    persons = mycursor.fetchall()

    return persons
