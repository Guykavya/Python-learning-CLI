from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

app = FastAPI()


class TeamOut(BaseModel):
    # TODO: allow reading attributes
    id: int
    name: str


class UserOut(BaseModel):
    # TODO: allow reading attributes
    id: int
    name: str
    email: str
    team: TeamOut | None = None


USERS: dict = {}


def to_out(user) -> UserOut:
    return UserOut.model_validate(user)


@app.get("/users/{user_id}")          # TODO: response_model, and 404 for an unknown id
def get_user(user_id: int):
    return {}
