from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

app = FastAPI()


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    team: TeamOut | None = None


USERS: dict = {}


def to_out(user) -> UserOut:
    return UserOut.model_validate(user)


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    user = USERS.get(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user
