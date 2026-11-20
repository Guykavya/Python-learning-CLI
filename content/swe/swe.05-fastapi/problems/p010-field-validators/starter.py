from fastapi import FastAPI
from pydantic import BaseModel, field_validator

DISPOSABLE = {"mailinator.com", "tempmail.dev", "10minutemail.com"}

app = FastAPI()


class SignupIn(BaseModel):
    name: str
    email: str
    interests: list[str] = []

    # TODO: a validator for name, one for email, and a mode="before" one for interests.
    # Remember: @field_validator(...) above @classmethod, and RETURN the cleaned value.


@app.post("/signups", status_code=201)
def signup(data: SignupIn):
    return data.model_dump()
