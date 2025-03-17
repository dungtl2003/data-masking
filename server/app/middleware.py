import logging
import jwt
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.preload import settings

logger = logging.getLogger("uvicorn")


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        global logger

        logger.debug(f"Request: {request.method} {request.url.path}")

        # Skip authentication for CORS preflight (OPTIONS)
        if request.method == "OPTIONS":
            return await call_next(request)

        url_path = request.url.path.rstrip("/")

        if url_path in [
            "/health",
            "/api/v1/auth/authorize",
            "/api/v1/auth/login",
            "/api/v1/auth/refresh",
            "/api/v1/auth/signup",
        ]:
            response = await call_next(request)
            return response

        if url_path.startswith("/api/v1/persons") and request.method in [
            "POST",
        ]:
            response = await call_next(request)
            return response

        # add your auth logic here
        auth_key = request.headers.get("Authorization")
        if auth_key is None:
            logger.debug("Unauthorized")
            return JSONResponse(status_code=401, content={"message": "Unauthorized"})

        components = auth_key.split(" ")
        if len(components) != 2:
            logger.debug(f"Invalid token: {auth_key} (the length is not 2)")
            return JSONResponse(
                status_code=401, content={"message": "Unauthorized token"}
            )

        if components[0] != "Bearer":
            logger.debug(f"Invalid token: {auth_key} (the type is not Bearer)")
            return JSONResponse(
                status_code=401, content={"message": "Unauthorized token"}
            )

        jwt_token = components[1]
        try:
            logger.debug(f"Decoding token: {jwt_token}")
            decoded_token = jwt.decode(
                jwt_token, settings.jwt_secret, algorithms=["HS256"]
            )
            id = int(str(decoded_token["id"]))
            request.state.user_id = id
        except jwt.ExpiredSignatureError:
            logger.debug(f"Token expired: {jwt_token}")
            return JSONResponse(status_code=401, content={"message": "Token expired"})
        except jwt.InvalidTokenError:
            logger.debug(f"Invalid token: {jwt_token}")
            return JSONResponse(status_code=401, content={"message": "Invalid token"})

        response = await call_next(request)
        return response
