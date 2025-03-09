from enum import Enum
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
