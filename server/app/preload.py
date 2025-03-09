import os
import pathlib
import sys
import mysql.connector


class Settings:
    def __init__(self):
        port = os.getenv("PORT")
        if port is not None and not port.isnumeric():
            raise ValueError("PORT must be a number")

        debug = os.getenv("DEBUG")
        if debug is not None and debug not in ["True", "False"]:
            raise ValueError("DEBUG must be a boolean")

        rounds = os.getenv("ROUNDS")
        if rounds is not None and not rounds.isnumeric():
            raise ValueError("ROUNDS must be a number")

        jwt_secret = os.getenv("JWT_SECRET")
        assert jwt_secret is not None, "JWT_SECRET must be provided"

        origins = os.getenv("ORIGINS")
        origins = [] if origins is None else origins.split(",")

        host = os.getenv("HOST")
        assert host is not None, "HOST must be provided"

        user = os.getenv("USER")
        assert user is not None, "USER must be provided"

        password = os.getenv("PASSWORD")
        assert password is not None, "PASSWORD must be provided"

        database = os.getenv("DATABASE")
        assert database is not None, "DATABASE must be provided"

        self.version = os.getenv("VERSION") or "v1"
        self.port = int(port) if port is not None else 8200
        self.debug = bool(debug) if debug is not None else False
        self.title = os.getenv("TITLE") or "FastAPI"
        self.description = os.getenv("DESCRIPTION") or "FastAPI application"
        self.rounds = int(rounds) if rounds is not None else 12
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.jwt_secret = jwt_secret
        self.origins = origins

        print(f"Settings: {self.__dict__}")


# remember to update the path when adding new modules
def resolve_path():
    curr_directory = str(pathlib.Path(__file__).parent.resolve())

    modules = [
        str(curr_directory),
        os.path.join(curr_directory, "api"),
        os.path.join(curr_directory, "api", "v1"),
        os.path.join(curr_directory, "api", "v1", "person"),
        os.path.join(curr_directory, "api", "v1", "auth"),
    ]

    [sys.path.append(module) if module not in sys.path else None for module in modules]


print("Resolving path")
resolve_path()

print("Loading settings")
settings = Settings()

print("Connecting to MySQL")
mydb = mysql.connector.connect(
    host=settings.host,
    user=settings.user,
    password=settings.password,
    database=settings.database,
)

os.environ["LOADED"] = "True"
