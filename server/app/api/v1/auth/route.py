import datetime
from types import NoneType
import bcrypt
from fastapi import APIRouter, Request
import logging
import jwt

from fastapi.responses import JSONResponse
from mysql.connector.types import RowType

from app.api.v1.auth.model import LoginModel
from app.preload import settings, mydb


api_router = APIRouter(prefix="/auth")


def create_token(id: int, username: str, duration: int):
    """
    create a token with the given data and duration (in hours)
    """
    iat = datetime.datetime.now(tz=datetime.timezone.utc)
    exp = iat + datetime.timedelta(hours=duration)

    return jwt.encode(
        {
            "id": id,
            "username": username,
            "iat": iat,
            "exp": exp,
        },
        settings.jwt_secret,
        algorithm="HS256",
    )


@api_router.post("/login")
async def login(login_data: LoginModel):
    logger = logging.getLogger("uvicorn")

    sql = "SELECT id, username, password FROM person WHERE email = %s"
    val = (login_data.email,)
    mycursor = mydb.cursor()
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    if (
        type(result) is not NoneType
        and type(result) is not RowType
        and type(result) is not tuple
    ):
        logger.debug(f"Invalid result type: {type(result)}")
        return JSONResponse(
            status_code=500, content={"message": "Internal server error"}
        )

    if not result or type(result) is NoneType:
        logger.debug("User not found")
        return JSONResponse(status_code=400, content={"message": "Auth failed"})

    # make it str
    hashed = str(result[2])
    password_bytes = login_data.password.encode("utf-8")
    hashed_bytes = hashed.encode("utf-8")

    if not bcrypt.checkpw(password_bytes, hashed_bytes):
        logger.debug("Invalid password")
        return JSONResponse(status_code=400, content={"message": "Auth failed"})

    id = int(str(result[0]))
    username = str(result[1])

    access_token = create_token(id, username, 1)
    refresh_token = create_token(id, username, 24)

    logger.debug("saving refresh token")
    sql = "INSERT INTO person_refresh_token (person_id, token) VALUES (%s, %s)"
    val = (id, refresh_token)
    mycursor.execute(sql, val)
    mydb.commit()

    response = JSONResponse(
        status_code=200,
        content={"access_token": access_token},
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=60 * 60 * 24,
    )

    return response


@api_router.get("/authorize")
async def authorize(request: Request):
    logger = logging.getLogger("uvicorn")

    auth_key = request.headers.get("Authorization")
    if auth_key is None:
        logger.debug("Unauthorized")
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})

    components = auth_key.split(" ")
    if len(components) != 2:
        logger.debug(f"Invalid token: {auth_key} (the length is not 2)")
        return JSONResponse(status_code=401, content={"message": "Unauthorized token"})

    if components[0] != "Bearer":
        logger.debug(f"Invalid token: {auth_key} (the type is not Bearer)")
        return JSONResponse(status_code=401, content={"message": "Unauthorized token"})

    jwt_token = components[1]
    try:
        logger.debug(f"Decoding token: {jwt_token}")
        jwt.decode(jwt_token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        logger.debug(f"Token expired: {jwt_token}")
        return JSONResponse(status_code=401, content={"message": "Token expired"})
    except jwt.InvalidTokenError:
        logger.debug(f"Invalid token: {jwt_token}")
        return JSONResponse(status_code=401, content={"message": "Invalid token"})

    return {"message": "Authorized"}


@api_router.get("/refresh")
async def refresh(request: Request):
    logger = logging.getLogger("uvicorn")

    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is None:
        logger.debug("Missing token")
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})

    decoded_token = None
    try:
        logger.debug(f"Decoding token: {refresh_token}")
        decoded_token = jwt.decode(
            refresh_token, settings.jwt_secret, algorithms=["HS256"]
        )
    except jwt.ExpiredSignatureError:
        logger.debug(f"Token expired: {refresh_token}")
        return JSONResponse(status_code=401, content={"message": "Token expired"})
    except jwt.InvalidTokenError:
        logger.debug(f"Invalid token: {refresh_token}")
        return JSONResponse(status_code=401, content={"message": "Invalid token"})

    id = int(str(decoded_token["id"]))
    username = str(decoded_token["username"])

    sql = "SELECT token FROM person_refresh_token WHERE token = %s"
    val = (refresh_token,)
    mycursor = mydb.cursor()
    mycursor.execute(sql, val)
    result = mycursor.fetchone()
    if not result or type(result) is NoneType:
        # this token maybe reused, so we need to clear all (force re-login)
        logger.debug(f"Token not found: {refresh_token}")
        logger.debug("Clearing all refresh tokens")
        sql = "DELETE FROM person_refresh_token WHERE person_id = %s"
        val = (id,)
        mycursor.execute(sql, val)
        mydb.commit()

        return JSONResponse(status_code=401, content={"message": "Invalid token"})

    # we just need to remove the token
    logger.debug(f"Removing refresh token {refresh_token}")
    sql = "DELETE FROM person_refresh_token WHERE token = %s"
    val = (refresh_token,)
    mycursor.execute(sql, val)
    mydb.commit()

    access_token = create_token(id, username, 1)
    refresh_token = create_token(id, username, 24)

    logger.debug("saving refresh token")
    sql = "INSERT INTO person_refresh_token (person_id, token) VALUES (%s, %s)"
    val = (id, refresh_token)
    mycursor.execute(sql, val)
    mydb.commit()

    response = JSONResponse(
        status_code=200,
        content={"token": access_token},
    )

    # save refresh token in cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=60 * 60 * 24,
    )

    return response


@api_router.get("/logout")
async def logout(request: Request):
    logger = logging.getLogger("uvicorn")

    refresh_token = request.cookies.get("refresh_token")
    if refresh_token is None:
        return JSONResponse(status_code=200, content={"message": "Logged out"})

    logger.debug(f"Removing refresh token {refresh_token}")
    sql = "DELETE FROM person_refresh_token WHERE token = %s"
    val = (refresh_token,)
    mycursor = mydb.cursor()
    mycursor.execute(sql, val)
    mydb.commit()

    response = JSONResponse(status_code=200, content={"message": "Logged out"})
    response.delete_cookie("refresh_token")

    return response
