from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI()


class UserCreate(BaseModel):                     # what clients send
    email: str
    password: str = Field(min_length=8)


class UserDB(BaseModel):                         # stands in for the database row
    id: int
    email: str
    password_hash: str


class UserOut(BaseModel):                        # what clients get back: no secrets declared
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str


FAKE_DB: dict[int, UserDB] = {}


def hash_password(password: str) -> str:
    return "pbkdf2$" + password[::-1]            # a stand-in; section 12.1 shows real hashing


@app.post("/users", response_model=UserOut, status_code=201)
def register(data: UserCreate):
    row = UserDB(id=len(FAKE_DB) + 1, email=data.email, password_hash=hash_password(data.password))
    FAKE_DB[row.id] = row
    return row


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    if user_id not in FAKE_DB:
        raise HTTPException(status_code=404, detail="user not found")
    return FAKE_DB[user_id]


@app.get("/users", response_model=list[UserOut])
def list_users():
    return [FAKE_DB[user_id] for user_id in sorted(FAKE_DB)]
