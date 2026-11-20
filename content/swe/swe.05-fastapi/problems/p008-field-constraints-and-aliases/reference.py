from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()


class SignupIn(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_name: str = Field(min_length=3, max_length=20, alias="userName")
    age: int = Field(ge=13, le=120)
    bio: str = Field(default="", max_length=50)


@app.post("/signups", status_code=201)
def signup(data: SignupIn):
    return data.model_dump()
