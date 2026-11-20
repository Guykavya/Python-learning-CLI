from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()


class SignupIn(BaseModel):
    # TODO: rules with Field(...), the alias "userName", and populate_by_name
    user_name: str
    age: int
    bio: str = ""


@app.post("/signups", status_code=201)
def signup(data: SignupIn):
    return data.model_dump()
