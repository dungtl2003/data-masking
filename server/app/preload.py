import os
import sys
import mysql.connector


class Settings:
    def __init__(self):
        master_key = os.getenv("MASTER_KEY")
        assert master_key is not None, "MASTER_KEY must be provided"

        subkey_rotation_counter = os.getenv("SUBKEY_ROTATION_COUNTER")
        if (
            subkey_rotation_counter is not None
            and not subkey_rotation_counter.isnumeric()
            and int(subkey_rotation_counter) < 0
        ):
            raise ValueError("SUBKEY_ROTATION_COUNTER must be a non-negative number")

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

        host = os.getenv("DB_HOST")
        assert host is not None, "DB_HOST must be provided"

        user = os.getenv("DB_USER")
        assert user is not None, "DB_USER must be provided"

        password = os.getenv("DB_PASSWORD")
        assert password is not None, "DB_PASSWORD must be provided"

        database = os.getenv("DB_DATABASE")
        assert database is not None, "DB_DATABASE must be provided"

        self.version = os.getenv("VERSION") or "v1"
        self.port = int(port) if port is not None else 8200
        self.debug = bool(debug) if debug is not None else False
        self.title = os.getenv("TITLE") or "FastAPI"
        self.description = os.getenv("DESCRIPTION") or "FastAPI application"
        self.rounds = int(rounds) if rounds is not None else 12
        self.db_host = host
        self.db_user = user
        self.db_password = password
        self.db_database = database
        self.jwt_secret = jwt_secret
        self.origins = origins
        self.master_key = bytes.fromhex(master_key)
        self.subkey_rotation_counter = (
            int(subkey_rotation_counter) if subkey_rotation_counter is not None else 5
        )

        print(f"Settings: {self.__dict__}")


# remember to update the path when adding new modules
# def resolve_path():
#     curr_directory = str(pathlib.Path(__file__).parent.resolve())
#
#     modules = [
#         str(curr_directory),
#         os.path.join(curr_directory, "api"),
#         os.path.join(curr_directory, "api", "v1"),
#         os.path.join(curr_directory, "api", "v1", "person"),
#         os.path.join(curr_directory, "api", "v1", "auth"),
#     ]
#
#     [sys.path.append(module) if module not in sys.path else None for module in modules]


# print("Resolving path")
# resolve_path()

print("pythonpath:", sys.path)

print("Loading settings")
settings = Settings()

print("Connecting to MySQL")
mydb = mysql.connector.connect(
    host=settings.db_host,
    user=settings.db_user,
    password=settings.db_password,
    database=settings.db_database,
    port=3306,
)
