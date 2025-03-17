from enum import Enum
from typing import TypedDict
from pydantic import BaseModel


class Gender(str, Enum):
    male = "male"
    female = "female"


class Person(BaseModel):
    email: str
    username: str
    password: str
    gender: Gender
    city: str = ""
    phone_number: str = ""

    class Config:
        use_enum_values = True


class EncryptedPerson(TypedDict):
    id: int
    email: str
    username: str
    password: bytes
    gender: bytes
    city: bytes
    phone_number: bytes
    private_key: bytes
    decrypt_frequency: bytes
