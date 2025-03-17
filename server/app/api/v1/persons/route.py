import logging
import secrets
from typing import List, cast
from fastapi import APIRouter, Request
import bcrypt
from fastapi.responses import JSONResponse
from mysql.connector.types import RowType

from app.api.v1.persons.model import EncryptedPerson, Person
from app.crypto.cipher import AES
from app.crypto.mode import GCMMode
from app.preload import mydb, settings


api_router = APIRouter(prefix="/persons")
logger = logging.getLogger("uvicorn")


def _encrypt_data(key: bytes, data: str) -> bytes:
    aes_cipher = AES(key)
    encrypt_cipher = GCMMode(aes_cipher)
    nonce = encrypt_cipher.nonce

    ciphertext, tag = encrypt_cipher.encrypt(data.encode("utf-8"))
    return nonce + ciphertext + tag


def _decrypt_data(key: bytes, data: bytes) -> str:
    """
    Data must be in the format of nonce + ciphertext + tag
    """
    nonce = data[:12]
    ciphertext = data[12:-16]
    tag = data[-16:]

    aes_cipher = AES(key)
    decrypt_cipher = GCMMode(aes_cipher, nonce)
    return decrypt_cipher.decrypt(ciphertext, tag).decode("utf-8")


@api_router.post("/", status_code=201)
async def create_user(person: Person):
    global logger

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
    logger.debug("encrypting data")

    master_key = settings.master_key
    private_key = secrets.token_bytes(32)

    # AES encryption
    encrypted_gender = _encrypt_data(private_key, person.gender)
    encrypted_city = _encrypt_data(private_key, person.city)
    encrypted_phone_number = _encrypt_data(private_key, person.phone_number)
    encrypted_private_key = _encrypt_data(master_key, private_key.hex())
    decrypt_frequency = 0
    encrypted_decrypt_frequency = _encrypt_data(private_key, str(decrypt_frequency))

    # bcrypt hashing
    password_bytes = person.password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=settings.rounds)
    hashed = bcrypt.hashpw(password_bytes, salt)

    logger.debug("creating user")

    mycursor = mydb.cursor()
    sql = "INSERT INTO person (email, username, password, gender, city, phone_number, private_key, decrypt_frequency) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (
        person.email,
        person.username,
        hashed,
        encrypted_gender,
        encrypted_city,
        encrypted_phone_number,
        encrypted_private_key,
        encrypted_decrypt_frequency,
    )
    mycursor.execute(sql, val)
    mydb.commit()

    return {"message": "User created"}


@api_router.get("/")
async def get_users(request: Request):
    global logger
    user_id: int = request.state.user_id

    logger.debug("getting users")
    mycursor = mydb.cursor(dictionary=True)

    mycursor.execute(
        "SELECT id, email, username, gender, city, phone_number, private_key, decrypt_frequency FROM person"
    )
    rows = mycursor.fetchall()
    encrypted_persons: List[EncryptedPerson] = [
        EncryptedPerson(**cast(EncryptedPerson, row)) for row in rows
    ]

    persons = []

    for encrypted_person in encrypted_persons:
        id = encrypted_person["id"]
        email = encrypted_person["email"]
        username = encrypted_person["username"]
        gender = encrypted_person["gender"].hex()
        city = encrypted_person["city"].hex()
        phone_number = encrypted_person["phone_number"].hex()

        # the only information that the user has permission to decrypt is their own
        if encrypted_person["id"] == user_id:
            logger.debug(f"decrypting data of user {id}")
            private_key = bytes.fromhex(
                _decrypt_data(settings.master_key, encrypted_person["private_key"])
            )
            gender = _decrypt_data(private_key, encrypted_person["gender"])
            city = _decrypt_data(private_key, encrypted_person["city"])
            phone_number = _decrypt_data(private_key, encrypted_person["phone_number"])
            decrypt_frequency = (
                int(_decrypt_data(private_key, encrypted_person["decrypt_frequency"]))
                + 1
            )

            if decrypt_frequency > settings.subkey_rotation_counter:
                logger.debug("rotating subkey")
                # rotate subkey
                decrypt_frequency = 0
                new_private_key = secrets.token_bytes(32)
                encrypted_private_key = _encrypt_data(
                    settings.master_key, new_private_key.hex()
                )
                new_encrypted_gender = _encrypt_data(new_private_key, gender)
                new_encrypted_city = _encrypt_data(new_private_key, city)
                new_encrypted_phone_number = _encrypt_data(
                    new_private_key, phone_number
                )
                new_encrypted_decrypt_frequency = _encrypt_data(
                    new_private_key, str(decrypt_frequency)
                )

                sql = "UPDATE person SET private_key = %s, gender = %s, city = %s, phone_number = %s, decrypt_frequency = %s WHERE id = %s"
                val = (
                    encrypted_private_key,
                    new_encrypted_gender,
                    new_encrypted_city,
                    new_encrypted_phone_number,
                    new_encrypted_decrypt_frequency,
                    id,
                )

                mycursor.execute(sql, val)
                mydb.commit()
            else:
                encrypted_decrypt_frequency = _encrypt_data(
                    private_key, str(decrypt_frequency)
                )
                sql = "UPDATE person SET decrypt_frequency = %s WHERE id = %s"
                val = (encrypted_decrypt_frequency, id)
                mycursor.execute(sql, val)
                mydb.commit()

        persons.append(
            {
                "id": id,
                "email": email,
                "username": username,
                "gender": gender,
                "city": city,
                "phone_number": phone_number,
            }
        )

    return persons
