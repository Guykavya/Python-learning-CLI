from fastapi import FastAPI
from pydantic import BaseModel, field_validator

DISPOSABLE = {"mailinator.com", "tempmail.dev", "10minutemail.com"}

app = FastAPI()


class SignupIn(BaseModel):
    name: str
    email: str
    interests: list[str] = []

    @field_validator("name")
    @classmethod
    def clean_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name must not be empty")
        return v.title()

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        v = v.strip().lower()
        local, at, domain = v.partition("@")
        if not local or not domain or "@" in domain:
            raise ValueError("not a valid email address")
        if domain in DISPOSABLE:
            raise ValueError("disposable email addresses are not allowed")
        return v

    @field_validator("interests", mode="before")
    @classmethod
    def split_interests(cls, v):
        if isinstance(v, str):
            return [part.strip() for part in v.split(",") if part.strip()]
        return v


@app.post("/signups", status_code=201)
def signup(data: SignupIn):
    return data.model_dump()
